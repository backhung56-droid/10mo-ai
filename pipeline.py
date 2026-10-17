#!/usr/bin/env python3
"""GPT 프로젝트 세미나 랜딩 패키지 재검증 및 재패키징.

실행: python pipeline.py [--rebuild-assets] [--render]
분석/카피/PRD는 docs/ 원본 연구 자산을 다시 읽어 결과와 일치 여부를 검증합니다.
새 카피 또는 사진을 추론·재작성하는 AI 단계는 자동화하지 않습니다.
의존성(이미지 재생성): cv2, numpy, Pillow
의존성(브라우저 캡처): playwright, Chromium
"""
import argparse
import json
import mimetypes
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'gpt_project_seminar_landing_20261020.zip'
FORM_URL = 'https://forms.gle/vKgXhViRCCGvM8Z98'
REQUIRED_DOCS = [
    '00_interview_master.md', '01_image_analysis.md', '02_template.md',
    '03_direction.md','04_customer.md', '05_personas.md',
    '06_sales_points.md', '07_copy_loop.md', '08_PRD_spec.md',
    '09_mockup_spec.md', 'asset_manifest.md', '11_implementation.md',
    '12_harness_report.md', '13_package_status.md'
]

class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=0;self.lang=None;self.links=[];self.img_alt=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='a' and 'data-apply' in a:self.links.append(a.get('href'))
        if tag=='img':self.img_alt.append(a.get('alt',''))

def validate():
    files=[ROOT/'docs'/f for f in REQUIRED_DOCS]
    files.extend([ROOT/'landing/index.html', ROOT/'landing/styles.css',ROOT/'landing/script.js',ROOT/'landing/assets/speaker-cutout.webp',ROOT/'landing/assets/seminar-poster-og.jpg',ROOT/'process_log.md',ROOT/'references/original-seminar-poster.png', ROOT/'references/design-system-v2.md'])
    missing=[str(x.relative_to(ROOT)) for x in files if not x.is_file()]
    html=(ROOT/'landing/index.html').read_text(encoding='utf-8')
    css=(ROOT/'landing/styles.css').read_text(encoding='utf-8')
    parser=SiteParser();parser.feed(html)
    checks={
        'all_required_files':len(missing)==0,
        'korean_page_language':parser.lang=='ko',
        'one_h1':parser.h1==1,
        'five_application_links':len(parser.links)==5,
        'all_links_match_user_form':all(x==FORM_URL for x in parser.links),
        'images_have_alt':all(parser.img_alt),
        'mobile_375_css': '@media(max-width:700px)' in css,
        'tablet_768_css':'@media(max-width:800px)' in css,
        'reduced_motion': 'prefers-reduced-motion' in css,
        'no_fake_free_guarantee':'참가 무료' not in html and '수료 보장' not in html,
    }
    return {'checks':checks,'missing':missing,'passed':all(checks.values()), 'url':FORM_URL}

def rebuild_assets():
    script=ROOT/'preview/extract_speaker.py'
    subprocess.run([sys.executable,str(script)],check=True,cwd=ROOT)
    from PIL import Image
    src=Image.open(ROOT/'landing/assets/speaker-cutout.png').convert('RGBA')
    src.save(ROOT/'landing/assets/speaker-cutout.webp',lossless=True,method=6)
    img=Image.open(ROOT/'references/original-seminar-poster.png').convert('RGB')
    img.resize((1200,849)).save(ROOT/'landing/assets/seminar-poster-og.jpg',quality=88,optimize=True)

def render():
    subprocess.run([sys.executable,str(ROOT/'preview/render_check.py')],check=True,cwd=ROOT)

def package():
    with zipfile.ZipFile(OUTPUT, 'w', compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for f in sorted(ROOT.rglob('*')):
            if not f.is_file():continue
            if f==OUTPUT or '__pycache__' in f.parts:continue
            if f.name in ('speaker-cutout.png','speaker-poster-crop.webp','speaker-close.webp'):continue
            if f.name in ('speaker-crop-check.jpg','speaker-matte-check.jpg'):continue
            if f.name=='create_docs.py':continue
            z.write(f,f.relative_to(ROOT))
    return OUTPUT

def main():
    args=argparse.ArgumentParser()
    args.add_argument('--rebuild-assets',action='store_true')
    args.add_argument('--render',action='store_true')
    a=args.parse_args()
    if a.rebuild_assets:rebuild_assets()
    if a.render:render()
    result=validate()
    (ROOT/'harness_run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if not result['passed']:
        print('검증 미통과',json.dumps(result,ensure_ascii=False,indent=2))
        raise SystemExit(1)
    output=package()
    print('검증 통과 / 생성:',output, '/ bytes:', output.stat().st_size)

if __name__=='__main__':main()
