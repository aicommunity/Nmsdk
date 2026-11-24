"""Digitize four red historical curves; preserve pixels and calibration uncertainty."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,OUT,save
SPECS=[('H111NL','f57e7053',[(62,9.1),(416,10.8)],'ВКР рисунок 15, обучение NL111, итерации 6–10'),
 ('H111NT','9266ab41',[(61,9.1),(413,10.8)],'ВКР рисунок 16, обучение NT111, итерации 6–10'),
 ('H129','4ed6e8b5',[(61,23.4),(413,25.2),(766,26.9)],'ВКР рисунок 17, обучение 22→129'),
 ('H37','f6b043a3',[(58,38.2),(410,39.9),(763,41.7)],'ВКР рисунок 18, обучение 22→37')]
def main():
    data=json.loads(PLAN.read_text(encoding='utf8'));curves=[]
    for ident,prefix,ticks,source in SPECS:
        asset=next(f for f in data['figures'] if f['asset'].startswith(prefix));file=Path(asset['preview']);im=np.array(Image.open(file).convert('RGB'))
        red=(im[:,:,0]>180)&(im[:,:,0].astype(int)-im[:,:,1]>80)&(im[:,:,0].astype(int)-im[:,:,2]>80)
        gray=(im[:,:,0]==im[:,:,1])&(im[:,:,1]==im[:,:,2])&(im[:,:,0]>185)&(im[:,:,0]<250)
        top=next(y for y,c in enumerate(gray[:,55:-3].sum(1)) if y>20 and c>(im.shape[1]-60)*.8)
        count=red[:,55:-3].sum(1);bottom=int(np.argmax(count[30:]))+30
        near=[y for y in range(bottom-1,bottom+3) if count[y]>=.9*count[bottom]];zero=float(np.median(near))
        pixels=np.array([p for p,t in ticks],dtype=float);times=np.array([t for p,t in ticks],dtype=float)
        matrix=np.column_stack([np.ones(len(pixels)),pixels]);inverse=np.linalg.pinv(matrix);intercept,slope=inverse@times
        residual=float(np.max(np.abs(matrix@np.array([intercept,slope])-times)));assert residual<=.05+abs(slope)
        scale=.09/(zero-top);points=[]
        for x in range(int(pixels[0]),im.shape[1]-2):
            ys=np.where(red[top:int(np.ceil(zero))+2,x])[0]+top
            if not len(ys):continue
            y=float(np.median(ys));weights=np.array([1.,float(x)])@inverse
            points.append({'pixel_x':x,'pixel_y':y,'pixel_y_min':int(ys.min()),'pixel_y_max':int(ys.max()),
                'time':float(intercept+slope*x),'potential':float(max(0,(zero-y)*scale)),
                'time_uncertainty':float(.05*np.abs(weights).sum()+abs(slope)),
                'potential_uncertainty':float(.0005+(.5*(ys.max()-ys.min())+1)*scale)})
        assert len(points)>500 and all(b['time']>a['time'] for a,b in zip(points,points[1:]))
        peak=max((p for p in points if p['time']<=points[0]['time']+.6),key=lambda p:p['potential'])
        curves.append({'id':ident,'source':source,'image':str(file),'source_asset_sha256':asset['asset'],'image_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
            'ticks':ticks,'voltage_top_pixel':top,'voltage_zero_pixel':zero,'voltage_max':.09,'time_intercept':float(intercept),'time_slope':float(slope),
            'tick_fit_max_residual':residual,'first_peak_time':peak['time'],'points':points,
            'uncertainty_note':'Time labels rounded to 0.1 s: ±0.05 s per tick, propagated through linear calibration; voltage labels ±0.0005 V plus red-stroke/pixel width. Median red pixel per image column; no amplitude fitting.'})
    save(OUT/'digitized-waves.json',curves);print([(c['id'],len(c['points']),c['tick_fit_max_residual']) for c in curves])
if __name__=='__main__':main()
