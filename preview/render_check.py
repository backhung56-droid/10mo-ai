from playwright.sync_api import sync_playwright
from pathlib import Path
import base64, mimetypes
root=Path(__file__).resolve().parent.parent
html=(root/'landing/index.html').read_text()
css=(root/'landing/styles.css').read_text()
script=(root/'landing/script.js').read_text()
html=html.replace('<link rel="stylesheet" href="styles.css">','<style>'+css+'</style>')
html=html.replace('<script src="script.js" defer></script>', '<script>'+script+'</script>')
for f in (root/'landing/assets').iterdir():
  mt=mimetypes.guess_type(str(f))[0]
  data='data:'+mt+';base64,'+base64.b64encode(f.read_bytes()).decode()
  html=html.replace('assets/'+f.name, data)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--allow-file-access-from-files','--no-proxy-server','--proxy-bypass-list=*','--disable-features=NetworkServiceSandbox'])
 for nm,w,h in [('pc',1280,900),('tablet',768,1024),('mobile',375,812),('small',320,700)]:
  page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda exc: errors.append(str(exc)))
  page.set_content(html,wait_until="load")
  page.screenshot(path=str(root/f'preview/{nm}-full.png'),full_page=True)
  page.screenshot(path=str(root/f'preview/{nm}-firstview.png'),full_page=False)
  d=page.evaluate('''() => ({title: document.title, lang:document.documentElement.lang, innerWidth:window.innerWidth, scrollWidth:document.documentElement.scrollWidth, hero:document.querySelector('.hero').getBoundingClientRect().toJSON(), cta:document.querySelector('.hero-action .button-main').getBoundingClientRect().toJSON(), image:document.querySelector('.hero-visual').getBoundingClientRect().toJSON(), ctaCount:[...document.querySelectorAll('[data-apply]')].length, links:[...document.querySelectorAll('[data-apply]')].map(x=>x.href), photo:document.querySelector('.speaker-picture img').complete, faq:document.querySelectorAll('.faq-list details').length})''')
  print(nm,w,h,d,'errors:',errors)
  page.close()
 browser.close()
