"""Comparable real-learning traces; keep uncertain historical prefixes explicit."""
from pathlib import Path
import sys,math,bisect
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,OLD,load
from training_report_data import lines

def collect():
 historical=load(OLD/'digitized-waves.json');result=[]
 for old_id,job,title,ident,mode in [('H111NT','trainer-111-trace','Обучение NT111 в итерациях с шестой по десятую','R21','cold'),
  ('H129','learner-22-to129-trace','Переход обучения от № 22 к № 129','R22','warm'),('H37','learner-22-to37-trace','Переход обучения от № 22 к № 37','R23','warm')]:
  folder=WORK/'runs/VT/traces'/(job+'-r1');meta=folder/'process.json'
  if not meta.exists() or load(meta)['status']!='completed':continue
  raw=lines(folder/'waveforms.jsonl');rs=lines(folder/'results.jsonl')
  if not rs or rs[0]['status']!='completed' or not raw:continue
  if mode=='cold':
   selected=[r for r in raw if 5<=r['iteration']<=9];first=[r for r in selected if r['iteration']==5]
   interpretation='Действительное обучение NT111, итерации 6–10. Амплитуда не нормирована; начало времени перенесено к первому максимуму.'
  else:
   cold=[r for r in raw if r['case']==job];last=max(r['iteration'] for r in cold)
   first=[r for r in cold if r['iteration']==last];selected=first+[r for r in raw if r['case']==job+'-stage-1']
   interpretation='Повторён реальный переход после холодного обучения № 22 с пятью последующими учебными периодами. Показан последний холодный период и пять новых. Точная предыстория исторического окна не установлена, поэтому это явно обозначенная реконструкция.'
  if not first or not selected:continue
  anchor=max(first,key=lambda r:r['soma_potential'][0])['time'];old=next(r for r in historical if r['id']==old_id)
  a=[(p['time']-old['first_peak_time'],p['potential']*1000) for p in old['points']];b=[(r['time']-anchor,r['soma_potential'][0]*1000) for r in selected]
  ax=[x for x,y in a];bx=[x for x,y in b]
  def interpolate(points,xs,t):
   j=bisect.bisect_left(xs,t)
   if j==0:return points[0][1] if t>=xs[0] else None
   if j>=len(points):return None
   x0,y0=points[j-1];x1,y1=points[j];return y0+(y1-y0)*(t-x0)/(x1-x0)
  lo=max(ax[0],bx[0]);hi=min(ax[-1],bx[-1]);step=.002;times=[i*step for i in range(math.ceil(lo/step),math.floor(hi/step)+1)]
  result.append({'id':ident,'title':title,'historical_id':old_id,'mode':mode,'source':old['source'],'source_image':old['image'],'source_image_sha256':old['image_sha256'],
   'historical_anchor_seconds':old['first_peak_time'],'new_anchor_seconds':anchor,'step_seconds':step,'rows':[[t,interpolate(a,ax,t),interpolate(b,bx,t)] for t in times],
   'historical_voltage_uncertainty_mV':max(p['potential_uncertainty'] for p in old['points'])*1000,'historical_time_uncertainty_seconds':max(p['time_uncertainty'] for p in old['points']),
   'interpretation':interpretation,'directory':str(folder),'raw_new_peak_mV':max(r['soma_potential'][0] for r in selected)*1000})
 return result
