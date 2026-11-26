from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
W,H=1440,480
S=2
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def font(n,b=False,m=False): return ImageFont.truetype(MONO if m else BOLD if b else FONT,n*S)
base=Image.new('RGB',(W*S,H*S))
a=np.zeros((H*S,W*S,3),dtype=np.uint8)
yy,xx=np.mgrid[0:H*S,0:W*S]
g=np.exp(-(((xx/S-1090)/300)**2+((yy/S-240)/230)**2))
for c,(lo,hi) in enumerate([(5,4),(10,13),(19,26)]): a[:,:,c]=lo+hi*g
base=Image.fromarray(a)
d=ImageDraw.Draw(base)
def text(x,y,t,size,color,b=False,m=False): d.text((x*S,y*S),t,font=font(size,b,m),fill=color)
d.line((48*S,40*S,1392*S,40*S),fill='#18364a',width=S)
d.line((48*S,440*S,1392*S,440*S),fill='#18364a',width=S)
text(70,76,'L L  /  SOFTWARE ENGINEER',14,'#87adc8',m=True)
text(62,141,'LUIS',78,'#f1f6fb',b=True)
text(290,141,'LEÓN',78,'#38b5ff',b=True)
text(70,246,'Backend & Business Software',25,'#d8e6f2')
d.line((70*S,300*S,118*S,300*S),fill='#43c4ff',width=3*S)
text(70,322,'Building software that solves',20,'#91a9bc')
text(70,352,'real problems.',20,'#e1effb',b=True)
text(70,409,'PYTHON  /  ODOO  /  POSTGRESQL  /  DOCKER',12,'#7299b4',m=True)
for x in range(702,1380,22):
    for y in range(62,424,22): d.ellipse((x*S,y*S,x*S+1,y*S+1),fill='#224055')
base=base.resize((W,H),Image.Resampling.LANCZOS)
CX,CY=1082,236
scale=.91
def tr(p): return (CX+p[0]*scale,CY+p[1]*scale)
# The mane is a faceted, symmetric silhouette, built from an outer and inner ring.
outer=[(0,-199),(53,-185),(86,-158),(126,-166),(144,-120),(176,-86),(168,-48),(194,-5),(177,43),(181,81),(145,107),(136,151),(91,161),(58,195),(0,220),(-58,195),(-91,161),(-136,151),(-145,107),(-181,81),(-177,43),(-194,-5),(-168,-48),(-176,-86),(-144,-120),(-126,-166),(-86,-158),(-53,-185)]
inner=[(0,-134),(35,-125),(61,-109),(88,-112),(91,-83),(107,-62),(103,-34),(113,-4),(100,27),(96,53),(81,76),(70,101),(47,113),(29,133),(0,146),(-29,133),(-47,113),(-70,101),(-81,76),(-96,53),(-100,27),(-113,-4),(-103,-34),(-107,-62),(-91,-83),(-88,-112),(-61,-109),(-35,-125)]
facets=[]
for i in range(len(outer)):
    j=(i+1)%len(outer)
    facets.append([outer[i],inner[i],inner[j]])
    facets.append([outer[i],inner[j],outer[j]])
# Recognizable feline face: ears, sloping brows, narrow eyes, broad muzzle and chin.
features=[
 [(-91,-84),(-93,-125),(-66,-110),(-65,-83)],
 [(91,-84),(93,-125),(66,-110),(65,-83)],
 [(-64,-92),(-36,-110),(0,-119),(36,-110),(64,-92)],
 [(-64,-92),(-81,-54),(-70,-13),(-43,5)],
 [(64,-92),(81,-54),(70,-13),(43,5)],
 [(-73,-44),(-45,-54),(-16,-33),(-26,-14),(-53,-19),(-73,-44)],
 [(73,-44),(45,-54),(16,-33),(26,-14),(53,-19),(73,-44)],
 [(-16,-33),(-11,6),(-23,27)],[(16,-33),(11,6),(23,27)],
 [(-70,-13),(-80,21),(-64,56),(-39,76)],
 [(70,-13),(80,21),(64,56),(39,76)],
 [(-23,27),(0,22),(23,27),(15,44),(0,51),(-15,44),(-23,27)],
 [(0,51),(0,66),(-23,79),(-49,72),(-59,55),(-43,33),(-23,27)],
 [(0,66),(23,79),(49,72),(59,55),(43,33),(23,27)],
 [(-49,72),(-32,106),(0,123),(32,106),(49,72)],
 [(-23,79),(0,87),(23,79)],
 [(0,-119),(0,-62)],
 [(-43,5),(-43,33)],[(43,5),(43,33)]
]
edges=[]
for f in facets+features:
    for p,q in zip(f,f[1:]): edges.append((p,q))
    if f in facets: edges.append((f[-1],f[0]))
# Seed particles along the actual drawing, so they assemble into the silhouette.
rng=random.Random(27)
particles=[]
for _ in range(390):
    p,q=rng.choice(edges); t=rng.random()
    target=tr((p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t))
    ang=rng.random()*math.tau; r=rng.uniform(120,330)
    origin=(CX+math.cos(ang)*r,CY+math.sin(ang)*r*.64)
    particles.append((target,origin,rng.random(),rng.uniform(.7,1.7)))

def smooth(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)
frames=[]
for frame in range(160):
    t=(frame/20+3.15)%8
    if t<2.4: assembly=smooth(t/2.4)
    elif t<5.5: assembly=1
    else: assembly=1-smooth((t-5.5)/2.5)
    structure=smooth((assembly-.50)/.50)
    art=Image.new('RGBA',(W*S,H*S)); ad=ImageDraw.Draw(art)
    light=Image.new('RGBA',(W*S,H*S)); ld=ImageDraw.Draw(light)
    def pts(poly): return [(int(tr(p)[0]*S),int(tr(p)[1]*S)) for p in poly]
    for k,tri in enumerate(facets):
        strength=int((22+(k%7)*4)*structure)
        ad.polygon(pts(tri),fill=(17,93,147,strength))
        ad.line(pts(tri+[tri[0]]),fill=(50,169,243,int(126*structure)),width=S)
    for poly in features:
        ad.line(pts(poly),fill=(106,207,255,int(230*structure)),width=2*S,joint='curve')
        ld.line(pts(poly),fill=(32,145,255,int(90*structure)),width=4*S)
    for sign in [-1,1]:
        eye=[(sign*59,-36),(sign*28,-29),(sign*37,-23),(sign*55,-25)]
        ad.polygon(pts(eye),fill=(169,243,255,int(255*structure)))
        ld.polygon(pts(eye),fill=(55,193,255,int(255*structure)))
    # A light wave travels through the existing geometry during the assembled hold.
    sweep=(t-2.4)/3.1
    if 0<sweep<1:
        scan=-210+450*sweep
        for p,q in edges:
            dist=abs((p[1]+q[1])/2-scan)
            a=int(220*max(0,1-dist/60)*structure)
            if a:
                ad.line(pts([p,q]),fill=(161,232,255,a),width=2*S)
                ld.line(pts([p,q]),fill=(38,164,255,a),width=5*S)
    for target,origin,seed,r in particles:
        a=smooth(max(0,min(1,(assembly-seed*.18)/.82)))
        x=origin[0]+(target[0]-origin[0])*a
        y=origin[1]+(target[1]-origin[1])*a
        x+=(1-a)*math.sin(t*1.3+seed*10)*9
        y+=(1-a)*math.cos(t*1.7+seed*10)*9
        alpha=int(70+150*a)
        ad.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=(71,184,255,alpha))
        if seed>.85: ld.ellipse(((x-3)*S,(y-3)*S,(x+3)*S,(y+3)*S),fill=(40,156,255,alpha))
    b=base.convert('RGBA')
    light=light.filter(ImageFilter.GaussianBlur(8*S)).resize((W,H),Image.Resampling.LANCZOS)
    art=art.resize((W,H),Image.Resampling.LANCZOS)
    b=Image.alpha_composite(b,light)
    b=Image.alpha_composite(b,art).convert('RGB')
    frames.append(b)
    if frame==10: b.save(ROOT/'leon-digital-preview.png')
# One shared palette keeps typography and backgrounds stable across frames.
pal=frames[10].quantize(colors=192,method=Image.Quantize.MEDIANCUT)
q=[im.quantize(palette=pal,dither=Image.Dither.NONE) for im in frames]
out=ROOT/'leon-digital-luis-leon.gif'
q[0].save(out,save_all=True,append_images=q[1:],duration=50,loop=0,disposal=1,optimize=True)
print(out, out.stat().st_size)
