"""Render already validated native declared-basin groups without running a model.

Run this scientific renderer only in an owned server analysis job. It translates
absolute recorded time by each observation's begin; no resampling, smoothing,
normalization, peak selection or certificate promotion is performed.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,sys
from pathlib import Path

SELECTED_OVERVIEWS={'basin_native0','basin_native7','basin_native8','basin_native9','basin_native10','basin_native13'}
SELECTED_CONTROLS={'basin_native0','basin_native7'}
COLORS=['#202f48','#dc563e','#2684a6','#238b45']
STYLES=['-','-','-','--']
VERSION=2

def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def reference(folder,name):
 path=Path(name)
 if path.is_absolute() or '..' in path.parts or ':' in name or '\\' in name:raise ValueError('unsafe_artifact_path')
 target=(folder/path).resolve(strict=True)
 if not target.is_relative_to(folder.resolve()):raise ValueError('artifact_outside_group')
 return target

def read_group(path,audit):
 record=load(path)
 if record['method']!='declared-window-basin-necessity-v1' or record['diagnostic_only'] is not True or record['training_certificate_eligible'] is not False:raise ValueError('unsupported_report_scope')
 if digest(path.read_bytes())!=audit['sha256'] or not audit['passed']:raise ValueError('record_not_bound_to_accepted_reader')
 folder=path.parent;binding=record['witness_binding'];ref=binding['group'];groupPath=reference(folder,ref['relative_path']);raw=groupPath.read_bytes()
 if len(raw)!=ref['bytes'] or digest(raw)!=ref['sha256']:raise ValueError('group_reference_changed')
 group=json.loads(raw);traces=[];n=record['geometry_policy']['maximum_inputs'];complete=binding['complete_group']
 if n!=2:raise ValueError('report_version_1_requires_two_input_fixture')
 if len(group['packets'])!=len(group['traces']):raise ValueError('packet_trace_count_changed')
 for index,(trace,packet) in enumerate(zip(group['traces'],group['packets'])):
  csvPath=reference(folder,trace['path']);raw=csvPath.read_bytes()
  if digest(raw)!=trace['sha256']:raise ValueError('primary_csv_changed')
  reader=csv.DictReader(io.StringIO(raw.decode('utf-8')));names=reader.fieldnames;somas=[k for k in names if k.startswith('soma')]
  if names!=['time','stimulus']+somas or len(somas)!=len(group['physical_channel_paths']):raise ValueError('csv_channels_changed')
  rows=[{key:float(value) for key,value in row.items()} for row in reader]
  if not rows or any(not math.isfinite(value) for row in rows for value in row.values()):raise ValueError('nonfinite_or_empty_primary')
  observed=packet['observation'];origin=observed['specification']['begin'];times=[row['time'] for row in rows]
  if any(b<=a for a,b in zip(times,times[1:])):raise ValueError('nonincreasing_primary_time')
  if index==0:role='Full before'
  elif complete and index==n+1:role='Full repeat'
  else:role='Omit input '+str(index-1)
  traces.append({'index':index,'role':role,'source':trace['path'],'sha256':trace['sha256'],'presented_ordinals':trace['presented_ordinals'],'absolute_origin_s':origin,'absolute_end_s':times[-1],'time_ms':[(time-origin)*1000 for time in times],'absolute_time_s':times,'stimulus':[row['stimulus'] for row in rows],'somas':[[row[key] for row in rows] for key in somas],'events':[{'id':e['id'],'absolute_s':e['time'],'relative_ms':(e['time']-origin)*1000} for e in observed['stimuli']]})
 if complete and len(traces)!=n+2:raise ValueError('complete_controls_missing')
 if audit['receipt']['complete_group']!=complete or audit['receipt']['training_certificate_eligible'] is not False:raise ValueError('reader_scope_changed')
 return record,group,traces

def render(corpus,audits,output,provenance):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 matplotlib.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'svg.hashsalt':provenance['primary_evidence_commit'],'savefig.facecolor':'white'})
 output.mkdir(parents=True,exist_ok=False);figures=output/'Figures';figures.mkdir();rows=[];images={};selected=[]
 def save(fig,name,include):
  fig.savefig(figures/(name+'.png'),dpi=150);fig.savefig(figures/(name+'.svg'));plt.close(fig)
  for suffix in ['.png','.svg']:
   path=figures/(name+suffix);images[path.relative_to(output).as_posix()]={'bytes':path.stat().st_size,'sha256':digest(path.read_bytes())}
  if include:selected.append('Figures/'+name+'.png')
 for audit in sorted(audits,key=lambda row:int(row['case'].removeprefix('basin_native'))):
  case=audit['case'];path=reference(corpus,audit['path']);record,group,traces=read_group(path,audit);full=traces[0];channels=group['physical_channel_paths'];count=len(channels);begin=record['window_begin_offset']*1000;end=record['window_end_offset']*1000
  extent=max(trace['time_ms'][-1] for trace in traces);margin=(end-begin)*.08;zoom=(max(0,begin-margin),min(extent,end+margin));geometry=record['geometry'];selectedCandidate=geometry['selected_candidate'] if geometry else None;peak=record['measured_maximum'];validity=record['geometry_validity'] or 'partial / rejected';title=path.parent.name.replace('_native_executor','').replace('_whole_burst_matched_omission_declared_basin','')
  def decorate(ax,channel,show_peak=True):
   ax.axvspan(begin,end,color='#98bce0',alpha=.17,zorder=0)
   if geometry and channel==record['channel']:
    for candidate in geometry['candidates']:
     left,right=candidate['left'],candidate['right'];t=full['time_ms'];lo=t[left['last_sample']];hi=t[right['first_sample']]
     ax.axvspan(lo,hi,color='#f0bf5c',alpha=.13,zorder=0)
     for anchor in [left,right]:ax.axvspan(t[anchor['first_sample']],t[anchor['last_sample']],color='#c58922',alpha=.35,zorder=1);ax.axvline(t[anchor['last_sample']],color='#c58922',alpha=.4,lw=.7)
     maximum=candidate['maximum'];x=(maximum['time']-full['absolute_origin_s'])*1000
     if show_peak:ax.plot(x,maximum['raw_potential'],marker='x',color='#8b6b19',ms=5,linestyle='None',zorder=5)
    if peak and show_peak:ax.plot((peak['time']-full['absolute_origin_s'])*1000,peak['raw_potential'],marker='*',color='#ae1d52',ms=12,linestyle='None',zorder=7)
   ax.grid(alpha=.2);ax.set_axisbelow(True)
  full_signal_low=min(0,min(full['stimulus']));full_signal_high=max(0,max(full['stimulus']));full_signal_span=max(full_signal_high-full_signal_low,1e-12)
  input_overlay_limits=(full_signal_low-.1*full_signal_span,full_signal_high+7*full_signal_span)
  def overlay_actual_full_input(ax):
   secondary=ax.twinx();secondary.step(full['time_ms'],full['stimulus'],where='post',color='#e67e16',lw=1.15,alpha=.9,zorder=2)
   secondary.set_ylim(input_overlay_limits);secondary.set_yticks(sorted(set([full_signal_low,full_signal_high])));secondary.set_ylabel('Full-before CSV input\nindependent raw scale',color='#b95c08',fontsize=8);secondary.tick_params(axis='y',labelcolor='#b95c08',labelsize=7)
   return secondary
  fig,axes=plt.subplots(count+1,2,figsize=(14,3+2.15*count),squeeze=False,sharex='col',gridspec_kw={'height_ratios':[1]*count+[.7]})
  limits=[]
  for channel,label in enumerate(channels):
   for column in range(2):
    ax=axes[channel,column]
    for trace in traces:ax.plot(trace['time_ms'],trace['somas'][channel],color=COLORS[trace['index']],ls=STYLES[trace['index']],lw=1.45,label=trace['role'])
    decorate(ax,channel);ax.set_ylabel(label+'\nraw potential');ax.set_xlim((0,extent) if column==0 else zoom)
    if column==1:
     values=[value for trace in traces for time,value in zip(trace['time_ms'],trace['somas'][channel]) if zoom[0]<=time<=zoom[1]]
     if values:
      low,high=min(values),max(values);padding=max((high-low)*.08,abs(high)*.01,1e-12);ax.set_ylim(low-padding,high+padding)
    secondary=overlay_actual_full_input(ax)
    if channel==0:ax.set_title(('Whole recorded trial' if column==0 else 'Declared-window zoom: independent local Y')+'; '+validity)
    limits.append({'channel':label,'panel':'overview' if column==0 else 'zoom','x_ms':list(ax.get_xlim()),'y_raw':list(ax.get_ylim()),'secondary_input_y_raw':list(secondary.get_ylim()),'secondary_input_role':'Full before actual CSV stimulus','secondary_input_csv_sha256':full['sha256'],'secondary_input_absolute_origin_s':full['absolute_origin_s']})
   axes[channel,0].legend(loc='best',ncol=2,fontsize=8)
  signal_values=[value for trace in traces for value in trace['stimulus']];signal_low=min(0,min(signal_values));signal_high=max(0,max(signal_values));signal_span=max(signal_high-signal_low,1e-12)
  for column in range(2):
   ax=axes[count,column]
   for trace in traces:
    ax.step(trace['time_ms'],trace['stimulus'],where='post',color=COLORS[trace['index']],ls=STYLES[trace['index']],lw=1.2,label=trace['role'])
    for event in trace['events']:
     y=signal_high+signal_span*(.12+.12*trace['index']);ax.plot(event['relative_ms'],y,marker='v',ms=4,color=COLORS[trace['index']]);ax.annotate(event['id'],(event['relative_ms'],y),xytext=(2,0),textcoords='offset points',fontsize=6,color=COLORS[trace['index']])
   ax.set_ylim(signal_low-.08*signal_span,signal_high+.65*signal_span);ax.set_ylabel('CSV stimulus\nraw units');ax.set_xlabel('Time from this probe observation.begin (ms)');ax.set_xlim((0,extent) if column==0 else zoom);ax.axvspan(begin,end,color='#98bce0',alpha=.17);ax.grid(alpha=.2)
  fig.suptitle(case+' | '+title+' | input '+str(record['assigned_input'])+' -> '+channels[record['channel']],fontsize=11,y=.99)
  fig.text(.01,.005,'Raw CSV, no smoothing/resampling/normalization. Blue: declared window; amber: recorded fixed basin/valleys; x: candidate; star: selected measurement. Orange on each soma: actual full-before CSV input (independent right scale). Diagnostic only; no training certificate.',fontsize=7)
  fig.tight_layout(rect=(0,.04,1,.96));save(fig,case+'-overview-and-zoom',case in SELECTED_OVERVIEWS)
  fig,axes=plt.subplots(len(traces),1,figsize=(14,2.5*len(traces)+.8),squeeze=False,sharex=True)
  for trace in traces:
   ax=axes[trace['index'],0];right=ax.twinx();right.step(trace['time_ms'],trace['stimulus'],where='post',color='#e67e16',lw=1.1,alpha=.9);right.set_ylim(signal_low-.1*signal_span,signal_high+7*signal_span);right.set_yticks(sorted(set([signal_low,signal_high])));right.set_ylabel('actual CSV input\nindependent raw scale',color='#b95c08');right.tick_params(axis='y',labelcolor='#b95c08')
   for channel,label in enumerate(channels):ax.plot(trace['time_ms'],trace['somas'][channel],label=label,lw=1.5,color=['#1b6d9b','#a9428f','#4b8c38'][channel%3])
   decorate(ax,record['channel'],show_peak=trace['index']==0)
   for event in trace['events']:ax.axvline(event['relative_ms'],color='#666666',ls=':',lw=.8);ax.text(event['relative_ms'],.9,event['id'],transform=ax.get_xaxis_transform(),fontsize=7)
   if peak:ax.axvline((peak['time']-full['absolute_origin_s'])*1000,color='#ae1d52',ls='--',lw=.7,alpha=.5)
   ax.set_title(trace['role']+'; presented inputs='+str(trace['presented_ordinals'])+'; absolute origin='+format(trace['absolute_origin_s'],'.8g')+' s',loc='left');ax.set_ylabel('raw potential');ax.legend(loc='upper right',fontsize=8);ax.set_xlim(0,extent)
  axes[-1,0].set_xlabel('Time from each probe observation.begin (ms)');fig.suptitle(case+' | Separate controls; all captured physical somas',fontsize=11);fig.text(.01,.005,'Full/omission/repeat are separate native probes. The source waveform is measured CSV stimulus; pulse labels use observed packet events. Peak and basin marks refer to the full-before geometry only.',fontsize=7);fig.tight_layout(rect=(0,.03,1,.97));save(fig,case+'-control-panels',case in SELECTED_CONTROLS)
  rows.append({'case':case,'title':title,'topology':'Branch' if title.startswith('Branch') else 'Classic','frequency_hz':group['packets'][0]['observation']['specification']['stimulus_profile']['frequency_hz'],'assigned_input':record['assigned_input'],'assigned_channel':record['channel'],'physical_channels':channels,'geometry_validity':record['geometry_validity'],'status':record['status'],'complete_group':record['witness_binding']['complete_group'],'trace_count':len(traces),'record_relative_path':audit['path'],'record_sha256':audit['sha256'],'declared_window_ms':[begin,end],'candidate_geometry_as_recorded':geometry,'selected_peak_as_recorded':peak,'axis_limits':limits,'traces':[ {key:value for key,value in trace.items() if key in ['index','role','source','sha256','presented_ordinals','absolute_origin_s','absolute_end_s','events']} for trace in traces],'figures':['Figures/'+case+'-overview-and-zoom.png','Figures/'+case+'-control-panels.png']})
 if len(rows)!=14 or len(selected)!=8 or sum(row['geometry_validity']=='valid' for row in rows)!=8 or sum(row['geometry_validity']=='ambiguous' for row in rows)!=2 or sum(not row['complete_group'] for row in rows)!=4:raise ValueError('unexpected_report_inventory')
 intro='''# Временные отклики: declared-window basin\n\nНабор содержит 14 технических групп: 8 допустимых назначений, 2 неоднозначных слитых отклика и 4 прерванные группы. Это новый проверочный набор, а не историческая матрица разделимости. Полные группы содержат Full before, по одному пропуску каждого входа и Full repeat. Для прерванных групп показаны только реально сохранённые пробы; отсутствующие контроли и геометрия не достраиваются.\n\nНа графиках показаны все физически записанные сомы. На каждую панель потенциала и её zoom наложен оранжевый ступенчатый измеренный сигнал Full before из столбца CSV stimulus; справа подписана независимая шкала исходных единиц входа. Высоты входа и потенциала не сравниваются по общей шкале. Нижняя панель сохраняет фактические входы всех записанных контролей. В отдельных контрольных панелях оранжевый вход относится именно к соответствующей пробе. Идентификаторы импульсов и их моменты взяты из observed packet events. Отдельные формы сигнала каждого физического входа не записывались: они не синтезируются из расписания.\n\nКаждая проба переводится из абсолютного времени в τ=(CSV time−observation.specification.begin)×1000 мс; исходные начала указаны в manifest. Кривые не интерполируются, не сглаживаются и не нормируются. Правая колонка использует отдельный локальный диапазон Y для каждой сомы. Голубая область — объявленное окно; янтарная — зафиксированный basin между записанными долинами; крестики — кандидаты; звезда — выбранное измерение. Эти отметки взяты из проверенной записи, алгоритм выбора в renderer не запускается.\n\nНезависимый Python replay подтвердил геометрию десяти полных групп и отсутствие продвижения четырёх неполных. Он не является подтверждением native causal lineage и не создаёт сертификат обучения.\n\n'''
 lines=[intro,'| Группа | Модель | Гц | Вход → канал | Результат | Проб |','|---|---|---:|---|---|---:|']
 for row in rows:lines.append('| '+row['case']+' | '+row['topology']+' | '+str(row['frequency_hz'])+' | '+str(row['assigned_input'])+' → '+str(row['assigned_channel'])+' | '+(row['geometry_validity'] or 'partial / rejected')+' | '+str(row['trace_count'])+' |')
 lines += ['','## Выбранные графики','']
 for name in selected:lines+=['!['+Path(name).stem+']('+name+')','']
 lines+=['## Полный серверный набор','','M40: `'+str(output)+'`. Для каждой из 14 групп сохранены overview+local-Y zoom и отдельные панели всех доступных контролей (PNG и SVG). Полные файлы перечислены с хешами в manifest.json.','','## Источники','','- C++ primary: `'+provenance['primary_evidence_commit']+'`.','- Python replay: `'+provenance['reader_evidence_commit']+'`; reader tool `'+provenance['reader_tool_root']+'`.','- Compiled root: `'+provenance['compiled_root']+'`; Pulse: `'+provenance['compiled_pulse']+'`.','- Renderer root: `'+provenance['renderer_root']+'`.','']
 markdown='\n'.join(lines);(output/'TemporalReport.ru.md').write_text(markdown,encoding='utf-8')
 import html
 cards=[]
 for row in rows:
  name=row['figures'][0];available=name in selected
  cards.append('<section><h2>'+html.escape(row['case']+' — '+row['title'])+'</h2><p>'+html.escape(str(row['trace_count'])+' recorded probes; '+str(row['geometry_validity'] or 'partial/rejected'))+'</p>'+(('<img src="'+name+'" alt="All soma overview and local Y zoom">') if available else '<p>Full figure retained on M40: '+html.escape(str(output/name))+'</p>')+'</section>')
 extra=''.join('<section><h2>'+html.escape(Path(name).stem)+'</h2><img src="'+name+'" alt="Individual native controls"></section>' for name in selected if name.endswith('control-panels.png'))
 document='<!doctype html><html lang="ru"><meta charset="utf-8"><title>Временные отклики declared basin</title><style>body{max-width:1300px;margin:30px auto;font:16px system-ui;color:#223}section{border-top:1px solid #ccd;padding-top:16px;margin-top:28px}img{width:100%;height:auto}pre{white-space:pre-wrap;font:15px system-ui;line-height:1.5}</style><h1>Временные отклики: declared-window basin</h1><pre>'+html.escape(intro.split('\n\n',1)[1])+'</pre>'+''.join(cards)+extra+'<h2>Источники</h2><pre>'+html.escape(json.dumps(provenance,indent=2,ensure_ascii=False))+'</pre></html>'
 (output/'Report.html').write_text(document,encoding='utf-8')
 for name in ['TemporalReport.ru.md','Report.html']:
  path=output/name;images[name]={'bytes':path.stat().st_size,'sha256':digest(path.read_bytes())}
 manifest={'kind':'declared_window_basin_temporal_report','schema_version':1,'renderer_version':VERSION,'provenance':provenance,'full_cache':str(output),'groups':rows,'files':images,'selected_git_figures':selected,'selected_git_figure_count':8,'full_group_count':14,'full_png_count':28,'full_svg_count':28,'transform':{'time':'tau_ms=(csv_absolute_time-observation.specification.begin)*1000 independently for each probe','potentials':'raw recorded values; no scaling/normalization/smoothing/resampling','stimulus':'raw measured CSV stimulus; aggregate/source signal, no invented per-input waveform','events':'observed packet events, not expected schedule','potential_input_overlay':'actual full-before CSV stimulus on every soma overview and zoom; original timestamps translated by that observed origin; independent labelled right raw-unit axis with visible height about one eighth; no synthetic per-input pulses','control_input_overlay':'each control panel uses that control own measured CSV stimulus on independently labelled right raw-unit axis','basin':'recorded full-before valley bounds: left.last_sample through right.first_sample; no recomputed selection','local_y':'per-channel min/max among all recorded controls inside zoom X range, plus explicit margin; exact limits recorded'},'environment':{'python':sys.version,'matplotlib':matplotlib.__version__,'backend':matplotlib.get_backend()},'new_cpp_or_model_execution':False,'native_causal_lineage_verified_by_python':False,'training_certificate_eligible':False,'scientific_verdict':None,'whole_plan_complete':False}
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');return manifest

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ['corpus','audits','output','primary-evidence-commit','reader-evidence-commit','compiled-root','compiled-pulse','reader-tool-root','renderer-root']:parser.add_argument('--'+name,required=True)
 args=parser.parse_args();provenance={name:getattr(args,name) for name in ['primary_evidence_commit','reader_evidence_commit','compiled_root','compiled_pulse','reader_tool_root','renderer_root']};result=render(Path(args.corpus).resolve(),load(Path(args.audits)),Path(args.output).resolve(),provenance);print(json.dumps({'groups':len(result['groups']),'selected_figures':len(result['selected_git_figures']),'output':str(Path(args.output).resolve()),'training_certificate_eligible':False}))
if __name__=='__main__':main()
