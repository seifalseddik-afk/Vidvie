#!/usr/bin/env bash
# usage: test/cmp.sh OUT.png  — renders test/compare.html next to the original lettering
SP=$(dirname "$1"); D=$(cd "$(dirname "$0")/.." && pwd)
node -e "
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:620,height:420}});
await p.goto('file://$D/test/compare.html');await p.waitForTimeout(400);await p.screenshot({path:'$SP/_mine.png'});await b.close();})();"
python3 - "$1" "$SP/_mine.png" <<'PY'
import sys
from PIL import Image, ImageDraw
U='/root/.claude/uploads/996fe185-3fe7-5ad6-accd-d2be3db74a89/'
o1=Image.open(U+'bc47a4b7-image.jpg').convert('RGB').crop((380,170,1000,360))
o2=Image.open(U+'e85d04e9-image.jpg').convert('RGB').crop((100,250,960,450)).resize((620,144))
orig=Image.new('RGB',(620,420),'white'); orig.paste(o1,(0,20)); orig.paste(o2,(0,240))
mine=Image.open(sys.argv[2]).convert('RGB')
c=Image.new('RGB',(1300,470),'white'); c.paste(orig,(660,40)); c.paste(mine,(10,40))
d=ImageDraw.Draw(c); d.text((900,10),'ORIGINAL',fill='black'); d.text((250,10),'RASIKH (traced with VectorCraft)',fill='black')
c.save(sys.argv[1])
PY
