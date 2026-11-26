from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from pathlib import Path
import numpy as np
import random, math

ROOT=Path(__file__).resolve().parent
W,H=1200,400
SCALE=W/1440
CX,CY=902,184
FPS=15
OUT=ROOT.parent/'leon-digital-stack-luis-leon.gif'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',28)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',11)
source=Image.open(ROOT.parent/'leon-digital-luis-leon.gif')
# Rebuild the original background and reuse its fixed personal-brand lettering.
yy,xx=np.mgrid[0:H,0:W]
g=np.exp(-(((xx/SCALE-1090)/300)**2+((yy/SCALE-240)/230)**2))
a=np.zeros((H,W,3),dtype=np.uint8)
for c,(lo,hi) in enumerate([(5,4),(10,13),(19,26)]): a[:,:,c]=lo+hi*g
base=Image.fromarray(a)
d=ImageDraw.Draw(base)
d.line((40,33,1160,33),fill='#18364a')
d.line((40,367,1160,367),fill='#18364a')
for x in range(585,1150,18):
    for y in range(52,354,18): d.point((x,y),fill='#224055')
source.seek(0)
lettering=source.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
base.paste(lettering.crop((0,0,555,H)),(0,0))

def smooth(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)
frames=[]
# Show the lion assembling, glowing, then scattering before the tool sequence.
for i in range(75):
    t=i/FPS/5*8
    source.seek(round(((t-3.15)%8)*20)%160)
    f=source.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    frames.append(f)

names=[('python','Python','LANGUAGE'),('postgresql','PostgreSQL','DATABASE'),('docker','Docker','CONTAINERS'),('flutter','Flutter','MULTIPLATFORM'),('odoo','Odoo','BUSINESS SOFTWARE')]
for scene,(slug,title,subtitle) in enumerate(names):
    raw=Image.open(ROOT/'assets'/f'{slug}.png').convert('RGBA')
    alpha=raw.getchannel('A')
    box=alpha.getbbox()
    alpha=alpha.crop(box)
    alpha.thumbnail((244,244),Image.Resampling.LANCZOS)
    iw,ih=alpha.size
    px,py=int(CX-iw/2),int(CY-ih/2)
    mask=Image.new('L',(W,H));mask.paste(alpha,(px,py))
    outline=mask.filter(ImageFilter.FIND_EDGES)
    # Node locations are sampled from the real vector silhouette.
    rng=random.Random(100+scene)
    solid=np.array(mask)
    edge=np.array(outline)
    ey,ex=np.where(edge>100)
    fy,fx=np.where(solid>180)
    particles=[]
    for j in range(440):
        if j<300:
            k=rng.randrange(len(ex));tx,ty=ex[k],ey[k]
        else:
            k=rng.randrange(len(fx));tx,ty=fx[k],fy[k]
        angle=rng.random()*math.tau;r=rng.uniform(160,255)
        ox=CX+math.cos(angle)*r;oy=CY+math.sin(angle)*r*.60
        particles.append((tx,ty,ox,oy,rng.random()))
    title_layer=Image.new('RGBA',(W,H))
    td=ImageDraw.Draw(title_layer)
    td.text((CX,326),title,font=font,fill='#e4f4ff',anchor='mm')
    td.text((CX,351),subtitle,font=small,fill='#789dbb',anchor='mm')
    # A cyan gradient stays inside the unaltered logo silhouette.
    rgb=np.zeros((H,W,4),dtype=np.uint8)
    rgb[:,:,0]=40+np.clip((yy-70)*.27,0,70).astype(np.uint8)
    rgb[:,:,1]=170+np.clip((yy-70)*.19,0,60).astype(np.uint8)
    rgb[:,:,2]=255
    rgb[:,:,3]=np.array(mask)
    icon=Image.fromarray(rgb)
    for i in range(60):
        t=i/FPS
        amount=smooth(t/1.35) if t<1.35 else (1 if t<2.65 else 1-smooth((t-2.65)/1.35))
        reveal=smooth((amount-.48)/.52)
        f=base.convert('RGBA')
        glow=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(glow)
        dots=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(dots)
        # A horizontal illumination band crosses the completed symbol.
        scan=-50+450*max(0,min(1,(t-1.35)/1.3))
        light_mask=np.clip(1-np.abs(yy-scan)/48,0,1)
        op=np.array(mask).astype(float)*reveal
        glowing=(op*(.18+.5*light_mask)).astype(np.uint8)
        halo=Image.new('RGBA',(W,H),(19,146,255));halo.putalpha(Image.fromarray(glowing))
        f=Image.alpha_composite(f,halo.filter(ImageFilter.GaussianBlur(12)))
        visible=icon.copy();visible.putalpha(Image.fromarray((op*(.65+.35*light_mask)).astype(np.uint8)))
        f=Image.alpha_composite(f,visible)
        for tx,ty,ox,oy,seed in particles:
            k=smooth((amount-seed*.12)/.88)
            x=ox+(tx-ox)*k+(1-k)*math.sin(t*1.5+seed*12)*8
            y=oy+(ty-oy)*k+(1-k)*math.cos(t*1.7+seed*10)*8
            opacity=int((60+140*k)*(1-.5*reveal))
            r=.8 if seed<.7 else 1.4
            dd.ellipse((x-r,y-r,x+r,y+r),fill=(117,222,255,opacity))
            if seed>.86:gd.ellipse((x-3,y-3,x+3,y+3),fill=(39,169,255,opacity))
        f=Image.alpha_composite(f,glow.filter(ImageFilter.GaussianBlur(5)))
        f=Image.alpha_composite(f,dots)
        label=title_layer.copy();label.putalpha(label.getchannel('A').point(lambda x:int(x*reveal)))
        f=Image.alpha_composite(f,label).convert('RGB')
        frames.append(f)
        if i==30:f.save(ROOT/f'preview-{slug}.png')
    print('Rendered',title,flush=True)

# Derive one shared palette from completed scenes to prevent color flicker.
montage=Image.new('RGB',(W,H*6))
for i,idx in enumerate([30,105,165,225,285,345]):montage.paste(frames[idx],(0,H*i))
palette=montage.quantize(colors=192,method=Image.Quantize.MEDIANCUT)
quantized=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
durations=[60 if i%3==0 else 70 for i in range(len(frames))]
quantized[0].save(OUT,save_all=True,append_images=quantized[1:],duration=durations,loop=0,optimize=True,disposal=1)
print('Saved',OUT,'bytes',OUT.stat().st_size,flush=True)
