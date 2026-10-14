/* Premium Drones Georgia — online payments through Bank of Georgia (card, Apple Pay, Google Pay).
   Cloudflare Pages "advanced mode" worker. GENERATED into dist/_worker.js by scripts/build-worker.py:
   edit scripts/worker.template.js, never dist/_worker.js. dist/_routes.json sends only /api/* here.

   Secrets live in Cloudflare (Pages > Settings > Variables and Secrets), never in these files:
     BOG_CLIENT_ID, BOG_CLIENT_SECRET   from Bank of Georgia Business Manager (required to switch payments on)
     BOG_PAYMENT_METHODS                optional, default "card,google_pay,apple_pay"
     ADMIN_KEY                          optional, opens /api/orders?key=... (needs the ORDERS binding)
     PAYMENTS_ENABLED = "off"           optional emergency switch
   Optional KV binding ORDERS keeps every order with the customer's name, phone and address.

   Rules: prices come from the catalog below (built from scripts/catalog.csv), never from the browser.
   Orders under RULES.threshold GEL are paid in full; larger orders pay RULES.depositPercent % online and
   the rest by bank transfer. An order counts as paid only when the bank's own receipt says "completed". */

const CATALOG = __CATALOG__;
const RULES = __RULES__;
const BOG_TOKEN_URL = 'https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token';
const BOG_API = 'https://api.bog.ge/payments/v1';
const LANGS = ['ka', 'en', 'ru'];
let cachedToken = null;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(request);
    try {
      const route = request.method + ' ' + url.pathname.replace(/\/+$/, '');
      if (route === 'GET /api/payments/config') return json(publicConfig(env));
      if (route === 'POST /api/checkout') return await checkout(request, env, url);
      if (route === 'GET /api/payments/status') return await status(env, url);
      if (route === 'POST /api/payments/callback') return await callback(request, env);
      if (route === 'GET /api/orders') return await orders(env, url);
      return json({ error: 'not_found' }, 404);
    } catch (err) {
      console.error('api error', err && err.stack || err);
      return json({ error: 'server_error' }, 500);
    }
  }
};

function json(data, code = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status: code,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex', ...extra }
  });
}

function enabled(env) {
  return Boolean(env.BOG_CLIENT_ID && env.BOG_CLIENT_SECRET && env.PAYMENTS_ENABLED !== 'off');
}

function methods(env) {
  const allowed = ['card', 'google_pay', 'apple_pay', 'bog_p2p', 'bog_loyalty', 'bnpl', 'bog_loan', 'gift_card'];
  const list = String(env.BOG_PAYMENT_METHODS || 'card,google_pay,apple_pay').split(',').map(s => s.trim()).filter(s => allowed.includes(s));
  return list.length ? list : ['card'];
}

function publicConfig(env) {
  return { enabled: enabled(env), threshold: RULES.threshold, depositPercent: RULES.depositPercent, currency: 'GEL' };
}

/* Order amount: full price under the threshold, otherwise a deposit (whole lari, kept under the threshold). */
function quote(items) {
  if (!Array.isArray(items) || items.length < 1 || items.length > 60) throw new UserError('bad_items');
  const lines = [];
  const seen = new Set();
  for (const it of items) {
    const sku = String(it && it.sku || '');
    const qty = Number(it && it.qty);
    if (!Object.prototype.hasOwnProperty.call(CATALOG, sku) || seen.has(sku)) throw new UserError('bad_items');
    if (!Number.isInteger(qty) || qty < 1 || qty > 100) throw new UserError('bad_items');
    seen.add(sku);
    const [name, price] = CATALOG[sku];
    lines.push({ sku, name, qty, price });
  }
  const total = lines.reduce((s, l) => s + l.price * l.qty, 0);
  const deposit = total >= RULES.threshold;
  const amount = deposit ? Math.min(Math.ceil(total * RULES.depositPercent / 100), RULES.threshold - 1) : total;
  return { lines, total, amount, mode: deposit ? 'deposit' : 'full' };
}

class UserError extends Error {}

function clean(value, max) {
  return String(value == null ? '' : value).replace(/[\u0000-\u001f\u007f<>]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
}

function orderRef() {
  const d = new Date();
  const ymd = d.toISOString().slice(2, 10).replace(/-/g, '');
  const rnd = crypto.getRandomValues(new Uint32Array(1))[0].toString(36).toUpperCase().padStart(6, '0').slice(-6);
  return `PDG-${ymd}-${rnd}`;
}

async function bogToken(env) {
  const now = Date.now();
  if (cachedToken && cachedToken.exp > now + 60000 && cachedToken.id === env.BOG_CLIENT_ID) return cachedToken.value;
  const res = await fetch(BOG_TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: 'Basic ' + btoa(`${env.BOG_CLIENT_ID}:${env.BOG_CLIENT_SECRET}`)
    },
    body: 'grant_type=client_credentials'
  });
  if (!res.ok) throw new Error('bog token ' + res.status);
  const data = await res.json();
  if (!data.access_token) throw new Error('bog token missing');
  // The docs call expires_in "seconds"; their sample looks like an epoch in ms. Accept all three forms.
  const e = Number(data.expires_in) || 300;
  const exp = e > 1e12 ? e : e > 1e9 ? e * 1000 : now + e * 1000;
  cachedToken = { value: data.access_token, exp, id: env.BOG_CLIENT_ID };
  return data.access_token;
}

async function checkout(request, env, url) {
  if (!enabled(env)) return json({ error: 'payments_off' }, 503);
  if (Number(request.headers.get('Content-Length') || 0) > 20000) return json({ error: 'too_large' }, 413);
  const origin = url.origin;
  const sentFrom = request.headers.get('Origin');
  if (sentFrom && sentFrom !== origin) return json({ error: 'bad_origin' }, 403);
  let input;
  try { input = await request.json(); } catch { return json({ error: 'bad_json' }, 400); }
  let q;
  try { q = quote(input && input.items); } catch (err) {
    if (err instanceof UserError) return json({ error: err.message }, 400);
    throw err;
  }
  const c = input.customer || {};
  const customer = { name: clean(c.name, 100), phone: clean(c.phone, 30), address: clean(c.address, 200) };
  if (customer.name.length < 2 || customer.phone.replace(/\D/g, '').length < 9) return json({ error: 'bad_customer' }, 400);
  const lang = LANGS.includes(input.lang) ? input.lang : 'ka';
  const ref = orderRef();
  const back = `${origin}${lang === 'ka' ? '' : '/' + lang}/payment?ref=${encodeURIComponent(ref)}`;
  const basket = q.mode === 'full'
    ? q.lines.map(l => ({ product_id: l.sku, description: l.name.slice(0, 120), quantity: l.qty, unit_price: l.price, total_price: l.price * l.qty }))
    : [{ product_id: 'DEPOSIT', description: `Deposit ${RULES.depositPercent}% for order ${ref} (total GEL ${q.total})`, quantity: 1, unit_price: q.amount, total_price: q.amount }];
  const body = {
    callback_url: `${origin}/api/payments/callback`,
    external_order_id: ref,
    application_type: 'web',
    capture: 'automatic',
    ttl: 30,
    buyer: { full_name: customer.name },
    purchase_units: { currency: 'GEL', total_amount: q.amount, basket },
    redirect_urls: { success: back, fail: back + '&r=fail' },
    payment_method: methods(env)
  };
  const token = await bogToken(env);
  const send = payload => fetch(`${BOG_API}/ecommerce/orders`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer ' + token,
      'Idempotency-Key': crypto.randomUUID(),
      'Accept-Language': lang === 'ka' ? 'ka' : 'en',
      Theme: 'light'
    },
    body: JSON.stringify(payload)
  });
  let res = await send(body);
  if (!res.ok && res.status >= 400 && res.status < 500) {
    // A method that is not yet activated in Business Manager can be refused: let the bank offer what is active.
    console.warn('bog order refused with methods, retrying without', res.status, await res.text());
    const { payment_method, ...rest } = body;
    res = await send(rest);
  }
  if (!res.ok) {
    console.error('bog order failed', res.status, await res.text());
    return json({ error: 'bank_error' }, 502);
  }
  const data = await res.json();
  const href = data && data._links && data._links.redirect && data._links.redirect.href;
  if (!data.id || !href || !/^https:\/\/([a-z0-9-]+\.)*bog\.ge\//.test(href)) {
    console.error('bog order unexpected response', JSON.stringify(data));
    return json({ error: 'bank_error' }, 502);
  }
  if (env.ORDERS) {
    const record = { ref, bogId: data.id, created: new Date().toISOString(), lang, mode: q.mode, total: q.total, amount: q.amount,
      items: q.lines, customer, status: 'created' };
    await env.ORDERS.put('order:' + ref, JSON.stringify(record), { expirationTtl: 60 * 60 * 24 * 730 });
    await env.ORDERS.put('bog:' + data.id, ref, { expirationTtl: 60 * 60 * 24 * 730 });
  }
  return json({ url: href, id: data.id, ref, mode: q.mode, total: q.total, amount: q.amount });
}

async function receipt(env, id) {
  const token = await bogToken(env);
  const res = await fetch(`${BOG_API}/receipt/${encodeURIComponent(id)}`, { headers: { Authorization: 'Bearer ' + token } });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error('bog receipt ' + res.status);
  return res.json();
}

async function remember(env, r) {
  if (!env.ORDERS || !r || !r.external_order_id) return;
  const key = 'order:' + r.external_order_id;
  const rec = await env.ORDERS.get(key, 'json');
  if (!rec) return;
  rec.status = r.order_status && r.order_status.key || rec.status;
  rec.paid = Number(r.purchase_units && r.purchase_units.transfer_amount) || 0;
  rec.method = r.payment_detail && r.payment_detail.transfer_method && r.payment_detail.transfer_method.key || rec.method || '';
  rec.updated = new Date().toISOString();
  await env.ORDERS.put(key, JSON.stringify(rec), { expirationTtl: 60 * 60 * 24 * 730 });
}

async function status(env, url) {
  if (!enabled(env)) return json({ error: 'payments_off' }, 503);
  let id = url.searchParams.get('id') || '';
  const ref = url.searchParams.get('ref') || '';
  if (!id && ref && env.ORDERS && /^PDG-\d{6}-[A-Z0-9]{6}$/.test(ref)) {
    const rec = await env.ORDERS.get('order:' + ref, 'json');
    id = rec && rec.bogId || '';
  }
  if (!/^[A-Za-z0-9-]{8,64}$/.test(id)) return json({ error: 'bad_id' }, 400);
  const r = await receipt(env, id);
  if (!r) return json({ status: 'unknown' }, 404);
  await remember(env, r);
  const pu = r.purchase_units || {};
  const items = Array.isArray(pu.items) ? pu.items : [];
  return json({
    status: r.order_status && r.order_status.key || 'unknown',
    ref: r.external_order_id || '',
    deposit: items.some(i => i && (i.product_id === 'DEPOSIT' || i.external_item_id === 'DEPOSIT')),
    amount: Number(pu.transfer_amount || pu.request_amount) || 0,
    currency: pu.currency_code || 'GEL'
  });
}

async function callback(request, env) {
  // The bank calls this after a payment. We never trust the body: we ask the bank for the receipt ourselves.
  const raw = await request.text();
  let id = '';
  try { const b = JSON.parse(raw); id = String(b && b.body && b.body.order_id || ''); } catch { /* ignore */ }
  if (/^[A-Za-z0-9-]{8,64}$/.test(id) && enabled(env)) {
    try { await remember(env, await receipt(env, id)); } catch (err) { console.error('callback receipt', err); }
  }
  return new Response('OK', { status: 200 });
}

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}

async function orders(env, url) {
  const key = url.searchParams.get('key') || '';
  if (!env.ADMIN_KEY || !env.ORDERS || key.length < 16 || key !== env.ADMIN_KEY) return json({ error: 'not_found' }, 404);
  const list = await env.ORDERS.list({ prefix: 'order:', limit: 200 });
  const recs = (await Promise.all(list.keys.map(k => env.ORDERS.get(k.name, 'json')))).filter(Boolean)
    .sort((a, b) => String(b.created).localeCompare(String(a.created)));
  const rows = recs.map(o => `<tr><td>${esc(o.created.slice(0, 16).replace('T', ' '))}</td><td>${esc(o.ref)}</td><td>${esc(o.status)}</td>`
    + `<td>${o.mode === 'deposit' ? 'deposit ' : ''}₾${esc(o.amount)} / ₾${esc(o.total)}</td><td>${esc(o.customer.name)}<br>${esc(o.customer.phone)}<br>${esc(o.customer.address)}</td>`
    + `<td>${o.items.map(i => esc(i.qty + ' × ' + i.name)).join('<br>')}</td></tr>`).join('');
  const page = `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>PDG orders</title><style>body{font:14px/1.45 system-ui,sans-serif;margin:16px;color:#1c1c1c}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}th{font-weight:600}</style>
<h1>PDG orders (${recs.length})</h1><p>Paid = status "completed". Deposit orders: the rest is paid by bank transfer.</p>
<div style="overflow-x:auto"><table><tr><th>Date (UTC)</th><th>Order</th><th>Status</th><th>Paid / total</th><th>Customer</th><th>Items</th></tr>${rows}</table></div>`;
  return new Response(page, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' } });
}
