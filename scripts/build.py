"""One command to rebuild and check the whole site:  python scripts/build.py"""
import subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts')); import pricing
def run(*a): 
    r=subprocess.run(list(a),cwd=ROOT)
    if r.returncode: sys.exit(r.returncode)
py=sys.executable
run(py,'scripts/build-shop.py'); run(py,'scripts/build-pages.py',pricing.SITE_URL); run(py,'scripts/build-search.py')
if shutil.which('node'):
    for f in ('content','script','shop','payments-config'): run('node','--check',f'dist/assets/js/{f}.js')
run(py,'scripts/verify-site.py'); print('BUILD OK')
