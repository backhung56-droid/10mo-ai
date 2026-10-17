import numpy as np,cv2
from PIL import Image
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'landing/assets'
src=cv2.imread(str(root/'references/original-seminar-poster.png'),cv2.IMREAD_COLOR)
h,w=src.shape[:2]
mask=np.zeros((h,w),np.uint8)
# Rough subject outline (probable foreground) in poster coordinates.
poly=np.array([(1135,142),(1192,130),(1255,139),(1325,170),(1370,225),(1390,300),(1390,373),(1370,444),(1355,485),(1380,503),(1425,532),(1490,625),(1490,1054),(615,1054),(643,952),(701,855),(766,761),(839,660),(914,578),(1005,505),(1040,466),(1015,415),(1000,350),(1015,280),(1044,217),(1080,171)],np.int32)
cv2.fillPoly(mask,[poly],cv2.GC_PR_FGD)
# probable BG at border around poly: not definite, to recover hair edge
cv2.polylines(mask,[poly],True,cv2.GC_PR_BGD,8)
# definite foreground areas
cv2.ellipse(mask,(1200,340),(114,151),0,0,360,cv2.GC_FGD,-1)
cv2.ellipse(mask,(1167,791),(288,180),0,0,360,cv2.GC_FGD,-1)
cv2.ellipse(mask,(1125,1002),(390,185),0,0,360,cv2.GC_FGD,-1)
# bg manually mark baked text as absolute background
mask[130:515,:997]=cv2.GC_BGD
# outside image right rect remain probable fg if touched border of image
bgdModel=np.zeros((1,65),np.float64);fgdModel=np.zeros((1,65),np.float64)
cv2.grabCut(src,mask,None,bgdModel,fgdModel,8,cv2.GC_INIT_WITH_MASK)
fg=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
# smooth small holes and feather outer edge to remove jaggedness
fg=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
fg=cv2.GaussianBlur(fg,(5,5),0.9)
rgba=cv2.cvtColor(src,cv2.COLOR_BGR2BGRA)
rgba[:,:,3]=fg
crop=rgba[130:1055,600:1491]
cv2.imwrite(str(out/'speaker-cutout.png'),crop)
# quick preview on white and gray
I=Image.open(out/'speaker-cutout.png').convert('RGBA')
bg=Image.new('RGB',I.size,(236,238,242));bg.paste(I,mask=I.getchannel('A'))
bg.resize((535,555)).save(str(root/'preview/speaker-matte-check.jpg'))
print('nontransparent',int((fg>0).sum()),'size',I.size)
