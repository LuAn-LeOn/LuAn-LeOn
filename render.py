from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
W,H,S = 1440,480,2
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def font(n,b=False,mono=False): return ImageFont.truetype(MONO if mono else BOLD if b else FONT,int(n*S))
def xy(p): return tuple(int(v*S) for v in p)
im=Image.new('RGB',(W*S,H*S))
pix=im.load()
for y in range(H*S):
    for x in range(W*S):
        g=math.exp(-(((x/S-1080)/430)**2+((y/S-240)/270)**2))
        pix[x,y]=(int(6+3*g),int(12+13*g),int(22+25*g))
d=ImageDraw.Draw(im)
def line(points,fill,width=1): d.line([xy(p) for p in points],fill=fill,width=width*S)
def text(p,s,n=16,fill='#92a9bf',bold=False,mono=False): d.text(xy(p),s,font=font(n,bold,mono),fill=fill)
def box(b,fill,outline,r=12,width=1): d.rounded_rectangle(xy(b),radius=r*S,fill=fill,outline=outline,width=width*S)
for x in range(708,1410,24):
    for y in range(48,438,24): d.ellipse(xy((x,y,x+1,y+1)),fill='#183046')
line([(28,28),(1412,28)],'#1a2b40')
line([(28,452),(1412,452)],'#1a2b40')
line([(28,28),(28,54)],'#279bef',2)
line([(1412,426),(1412,452)],'#279bef',2)
box((64,65,112,113),'#0a1929','#23577d',10)
text((73,74),'LL',23,'#72c9ff',True)
text((130,79),'LUIS LEÓN / SOFTWARE ENGINEER',15,'#a9bfd1',mono=True)
text((60,140),'LUIS',76,'#f0f6fc',True)
text((283,140),'LEÓN',76,'#35aaff',True)
text((66,239),'Backend & Business Software',26,'#d0dfed')
line([(67,295),(110,295)],'#35aaff',3)
text((66,316),'Building software that solves',21,'#91a9be')
text((66,347),'real problems.',21,'#d7e9f8',True)
text((66,409),'PYTHON  /  ODOO  /  POSTGRESQL  /  DOCKER',13,'#7195b2',mono=True)

# These traces are a visual metaphor, not production telemetry.
paths=[[(881,142),(948,142),(948,238),(989,238)],
       [(1131,238),(1186,238),(1186,142),(1211,142)],
       [(1211,163),(1200,163),(1200,259),(1131,259)],
       [(989,259),(932,259),(932,338),(889,338)],
       [(1060,277),(1060,338),(1211,338)],
       [(810,299),(810,219),(883,219),(883,161)]]
for p in paths: line(p,'#224a67',2)
# Two quiet L-shaped circuit traces serve as the personal signature.
for p in [[(740,92),(740,389),(941,389)],[(760,92),(760,410),(961,410)]]:
    line(p,'#15364f',1)

def node(cx,cy,label,sub,kind):
    bw=142 if kind=='core' else 150
    bh=78
    box((cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2),'#0b1b2b','#31729c' if kind=='core' else '#254760',12)
    if kind=='core':
        text((cx-56,cy-29),'</>',16,'#46baff',mono=True)
    elif kind=='db':
        d.ellipse(xy((cx-58,cy-25,cx-35,cy-17)),outline='#54c5f2',width=2*S)
        line([(cx-58,cy-21),(cx-58,cy-5)],'#54c5f2',2)
        line([(cx-35,cy-21),(cx-35,cy-5)],'#54c5f2',2)
        d.arc(xy((cx-58,cy-10,cx-35,cy-2)),0,180,fill='#54c5f2',width=2*S)
    elif kind=='docker':
        for xx,yy in [(0,0),(9,0),(18,0),(9,-9),(18,-9)]:
            d.rectangle(xy((cx-58+xx,cy-15+yy,cx-52+xx,cy-9+yy)),fill='#54c5f2')
    else: text((cx-59,cy-29),'{}' if kind=='api' else 'oo',19,'#54c5f2',mono=True)
    text((cx-57,cy+6),label,18,'#e0edf8',True)
    text((cx-20,cy-25),sub,10,'#789bb8',mono=True)
node(806,142,'API','REQUEST','api')
node(1060,248,'Python','PROCESS','core')
node(1286,142,'PostgreSQL','STORE','db')
node(814,338,'Odoo','BUSINESS','odoo')
node(1286,338,'Docker','DEPLOY','docker')
text((1000,67),'ARCHITECTURE IN MOTION',12,'#6f9cbd',mono=True)
text((1000,407),'BUILD. CONNECT. SOLVE.',12,'#6f9cbd',mono=True)
base=im.resize((W,H),Image.Resampling.LANCZOS)

def position(points,t):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
    target=t*sum(lengths)
    for a,b,n in zip(points,points[1:],lengths):
        if target<=n: return (a[0]+(b[0]-a[0])*target/n,a[1]+(b[1]-a[1])*target/n)
        target-=n
    return points[-1]

frames=[]
for i in range(160):
    frame=base.copy().convert('RGBA')
    glow=Image.new('RGBA',(W,H)); gd=ImageDraw.Draw(glow)
    sharp=Image.new('RGBA',(W,H)); sd=ImageDraw.Draw(sharp)
    for j,p in enumerate(paths):
        phase=(i/160*2-j*.145)%1
        for k in range(16):
            t=phase-k*.012
            if t<0: continue
            x,y=position(p,t)
            alpha=int(220*(1-k/16)**1.8)
            gd.ellipse((x-5,y-5,x+5,y+5),fill=(32,166,255,alpha))
            sd.ellipse((x-1.7,y-1.7,x+1.7,y+1.7),fill=(91,209,255,alpha))
        x,y=position(p,phase)
        sd.ellipse((x-2.4,y-2.4,x+2.4,y+2.4),fill=(210,247,255,255))
    # A slow halo ties the central processing node to the travelling signals.
    pulse=(math.sin(2*math.pi*i/80)+1)/2
    gd.rounded_rectangle((987,207,1133,289),radius=14,outline=(45,171,255,int(45+60*pulse)),width=3)
    frame=Image.alpha_composite(frame,glow.filter(ImageFilter.GaussianBlur(7)))
    frame=Image.alpha_composite(frame,sharp).convert('RGB')
    frames.append(frame)
    if i==25: frame.save(OUT/'arquitectura-viva.png')
palette=frames[25].quantize(colors=192,method=Image.Quantize.MEDIANCUT)
q=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
q[0].save(OUT/'arquitectura-viva.gif',save_all=True,append_images=q[1:],duration=50,loop=0,optimize=True,disposal=1)
print('Created',OUT/'arquitectura-viva.gif')
print('Bytes:',(OUT/'arquitectura-viva.gif').stat().st_size)
