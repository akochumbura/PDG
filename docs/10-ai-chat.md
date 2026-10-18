# AI live chat (PDG assistant)

What it is: a chat button at the bottom right of every page. Visitors ask questions in Georgian, English or Russian;
Claude (Anthropic) answers using only PDG's own facts: products and prices from scripts/catalog.csv, dist/llms.txt,
the FAQ, terms, service and academy texts. These are built into dist/_worker.js on every `python scripts/build.py`,
so a price change in the catalog reaches the chat automatically.

Rules it follows (scripts/worker.template.js, chatSystem): answers in the visitor's language, short; never invents prices,
stock, delivery dates or discounts; cannot take orders or payments; no pesticide dosage advice; fair about other brands;
hands over to a person on WhatsApp +995 550 00 43 33. A "Talk to a person on WhatsApp" link is always under the chat.

Status: built and tested with a simulated AI. It stays hidden until the key is set.

To switch it on:
1. console.anthropic.com -> create an account for the company, add a payment method, create an API key.
   Set a monthly spend limit there (for example 20-50 USD).
2. Cloudflare Pages -> the site -> Settings -> Variables and Secrets -> add ANTHROPIC_API_KEY (Encrypt).
   Optional: CHAT_MODEL (default claude-haiku-5-5), CHAT_DAILY_LIMIT (default 400 replies a day; needs the KV binding).
3. Optional KV namespace bound as PDG_DATA (same one used by orders and accounts) for the daily limit.
4. Upload the site again (or redeploy) so the setting takes effect.
To stop it at once: add CHAT_ENABLED = off.

Limits built in: 20 replies per visitor per 10 minutes, 16 messages of history, answers up to ~700 tokens.
Privacy: conversations stay in the visitor's browser tab and go to the AI service only to get an answer; nothing is stored by PDG.

## Website chat first (2026-10-14)

The chat button ("მოგვწერეთ") opens a chat that stays on the website.

- Visitor messages are saved in the PDG_DATA storage. Without PDG_DATA the chat only shows WhatsApp / Messenger / phone.
- With ANTHROPIC_API_KEY set, the AI answers at once. Without it, the visitor is asked for a phone or email and the team answers.
- **Team inbox:** open `https://premium-drones.ge/api/chat/inbox?key=YOUR_ADMIN_KEY` on your phone (bookmark it). New chats are marked NEW. Type a reply and tap "Send reply": the visitor sees it in the website chat within seconds, or when they come back. After the team replies, the AI stops answering that chat.
- WhatsApp, Messenger and phone are shown as "other options" only after the visitor's first message.
- Optional alert on a new chat: create a Telegram bot with @BotFather, then add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as secrets in Cloudflare.


## WhatsApp alert for new chat messages
1. Save the CallMeBot WhatsApp number (shown on callmebot.com, WhatsApp API page) in your phone contacts.
2. Send it the WhatsApp message: I allow callmebot to send me messages
3. You get a reply with your apikey.
4. Cloudflare → Workers & Pages → pdg → Settings → Variables and secrets → add two Secrets:
   WHATSAPP_ALERT_PHONE = your number with country code, e.g. +995550004333
   WHATSAPP_ALERT_KEY = the apikey
5. Deployments → ⋯ → Retry deployment.
The alert comes once per conversation when a visitor writes after you last read it; the key is never in the alert.
CallMeBot is a free third-party service for personal alerts (no guarantee); the official alternative is Meta's WhatsApp Business Cloud API.

## AI on every message + learning from the team (2026-10-14)
- With ANTHROPIC_API_KEY set, the AI answers every visitor message. After a team reply in a chat, the AI pauses in that chat for 30 minutes, then answers again.
- Learning: every team reply from the inbox is saved with the visitor's question (KV key `learn:index`, newest 80). The AI treats these as trusted PDG answers and reuses them for similar questions. Switch off with LEARN_ENABLED = off.
- PDG facts (prices, stock, delivery, warranty, specs) only from KNOWLEDGE and team answers; general drone/agronomy questions from the model's general knowledge. Still no pesticide dosages.
- This is not model training: the model itself does not change; it reads these answers each time.
- Inbox: https://premium-drones.ge/api/chat/inbox shows a sign-in box (keys with + # & work); spaces around the key are ignored.

## Telegram alerts (18 Oct 2026, recommended; CallMeBot had no free slots)
1. Telegram → @BotFather → /newbot → choose a name and a username ending in "bot" → copy the token.
2. Cloudflare → pdg → Settings → Variables and secrets → add Secret TELEGRAM_BOT_TOKEN = the token → Deployments → ⋯ → Retry deployment.
3. Open your new bot in Telegram and press Start.
4. Open https://premium-drones.ge/api/telegram/setup and sign in with ADMIN_KEY: the site saves your chat (KV tg:chat) and sends a test message.
New chat conversations (and new messages after you read a conversation) and consultation requests then arrive in Telegram with the inbox link.
