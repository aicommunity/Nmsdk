"""Render scientific figures on .15 from an independently verified sealed analysis."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import traceback

def require(value,reason):
    if not value:raise RuntimeError(reason)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('data-root','analysis-pointer','archive-adapter','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    for name in ('archive-id','archive-adapter-sha256'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();sys.dont_write_bytecode=True
    require(os.name=='nt' and socket.gethostname().upper()=='AQUA3060','server15_required')
    adapter_path=args.archive_adapter.resolve(strict=True)
    require(sha(adapter_path)==args.archive_adapter_sha256,'archive_adapter_changed')
    spec=importlib.util.spec_from_file_location('axon_figure_archive',adapter_path)
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    data,_,_=adapter.root_identity(args.data_root,args.archive_id);output=args.output.resolve()
    require(output.is_relative_to(data/'Experiments') and not output.exists(),'fresh_figure_output_required')
    output.mkdir(parents=True,exist_ok=False)
    result={'kind':'axone_conduction_figures','schema_version':1,'analysis_complete':False,
            'producer_sha256':sha(Path(__file__)),'archive_id':args.archive_id,'scientific_verdict':None,
            'model_executed':False,'auxiliary_process_provenance':'not_captured'}
    try:
        adapter.verify(argparse.Namespace(data_root=data,archive_id=args.archive_id,verify_pointer=args.analysis_pointer,
                                         maximum_bytes=4*1024**3,maximum_files=20000))
        pointer=read(args.analysis_pointer)
        require(pointer['status']['role']=='analysis' and pointer['status']['analysis_complete'] is True,'verified_analysis_required')
        source=(data/pointer['attempt_relative']).resolve(strict=True);document=read(source/'result.json')
        require(document['kind']=='axone_conduction_matrix_analysis' and document['mode']=='burst' and
                document['analysis_complete'] is True and len(document['rows'])==60,'full_burst_analysis_required')
        rows=document['rows'];require(all(row['capture_valid'] for row in rows),'invalid_capture_in_figure_input')
        os.environ['MPLCONFIGDIR']=str(data/'PythonPackageCache'/'matplotlib3107')
        import matplotlib
        require(matplotlib.__version__=='3.10.7','declared_matplotlib_version_required')
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'svg.fonttype':'none'})
        files=[]
        def save(figure,name):
            figure.canvas.draw()
            for extension in ('png','svg'):
                path=output/(name+'.'+extension);require(not path.exists(),'figure_output_exists')
                figure.savefig(path,dpi=200,bbox_inches='tight',facecolor='white')
                require(path.stat().st_size>1000,'empty_figure');files.append({'name':path.name,'bytes':path.stat().st_size,'sha256':sha(path)})
            plt.close(figure)
        carriers=('NAxoneChain','NAxoneChainAndDelay');frequencies=(20000,40000,100000)
        lookup={(row['carrier'],row['frequency_hz'],row['segments'],row['pattern']):row for row in rows}
        require(len(lookup)==60,'duplicate_figure_case')
        figure,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
        for ax,carrier in zip(axes,carriers):
            for frequency in frequencies:
                points=[lookup[carrier,frequency,n,'single'] for n in (1,3,7,15,31)]
                require(all(p['association']['complete_one_to_one'] and len(p['association']['certain_lags_s'])==1 for p in points),
                        'single_event_latency_not_identified')
                ax.plot([p['segments'] for p in points],[1000*p['association']['certain_lags_s'][0] for p in points],
                        marker='o',markersize=4,label=f'{frequency//1000} кГц')
            ax.set(title=carrier,xlabel='Число сегментов',ylabel='Разность фронтов, мс');ax.grid(alpha=.25);ax.legend(frameon=False)
        figure.suptitle('Одиночный импульс: измеренная задержка')
        save(figure,'single_latency_vs_length')
        patterns=('span25','span480','m4_isi2ms','m4_isi5ms','m16_isi2ms')
        labels={'span25':'Ист. 25','span480':'Ист. 480','m4_isi2ms':'M4 / 2','m4_isi5ms':'M4 / 5','m16_isi2ms':'M16 / 2'}
        cells=[[lookup[carrier,f,3,pattern] for f in frequencies for pattern in patterns] for carrier in carriers]
        ratios=[[p['output_count']/p['input_count'] for p in line] for line in cells]
        figure,ax=plt.subplots(figsize=(13,3.5),layout='constrained')
        ax.imshow(ratios,vmin=0,vmax=max(1.,max(max(line) for line in ratios)),cmap='Blues',aspect='auto')
        for y,line in enumerate(cells):
            for x,p in enumerate(line):
                ambiguous=p['association']['ambiguous'];text=f"{p['output_count']}/{p['input_count']}"+('*' if ambiguous else '')
                ax.text(x,y,text,ha='center',va='center',color='white' if ratios[y][x]>.6 else 'black')
                if p['association']['complete_one_to_one']:ax.add_patch(Rectangle((x-.49,y-.49),.98,.98,fill=False,lw=1.5,edgecolor='#2b8c58'))
        ax.set_xticks(range(15),[f'{labels[p]}\n{f//1000} кГц' for f in frequencies for p in patterns],rotation=40,ha='right')
        ax.set_yticks(range(2),carriers);ax.set_title('Число фронтов выхода / число фронтов входа, три сегмента')
        figure.supxlabel('* Неоднозначная временная связь. Рамка: полная однозначная связь. Количество само по себе её не доказывает.',fontsize=9)
        save(figure,'burst_event_counts')
        figure,axes=plt.subplots(2,2,figsize=(10,6),layout='constrained')
        for y,carrier in enumerate(carriers):
            for x,pattern in enumerate(('span25','m16_isi2ms')):
                p=lookup[carrier,20000,3,pattern];ax=axes[y,x]
                groups=[p['source_events']]+[s['events'] for s in p['segment_events']]
                for level,events in enumerate(groups):
                    times=[event['onset_tick']/20. for event in events]
                    ax.vlines(times,level-.25,level+.25,color=('black' if level==0 else '#2878a0'),linewidth=1.5)
                ax.set_yticks(range(4),['Источник','Сегмент 1','Сегмент 2','Сегмент 3'])
                ax.set(xlim=(0,50),ylim=(3.6,-.6),xlabel='Время от начала пробы, мс',title=f'{carrier}\n{labels[pattern]}, 20 кГц')
                ax.grid(axis='x',alpha=.2)
        figure.suptitle('Фактические фронты коротких пачек; причинные пары не назначены')
        save(figure,'dense_burst_event_rasters')
        versions={name:importlib.metadata.version(name) for name in ('matplotlib','numpy','Pillow','contourpy','fonttools','kiwisolver')}
        result.update(analysis_complete=True,files=files,renderer={'python':sys.version,'executable':sys.executable,
            'backend':matplotlib.get_backend(),'versions':versions},input_result_sha256=sha(source/'result.json'),
            input_archive_manifest_sha256=pointer['manifest']['sha256'],source_commit=document['source_commit'],
            claim_scope='Plots of verified observations; no additional physical run, causal assignment, learning or carrier acceptance.')
    except BaseException as error:result.update(error=str(error),traceback=traceback.format_exc())
    write(output/'result.json',result)
    print(json.dumps({'analysis_complete':result['analysis_complete'],'figures':len(result.get('files',[])),
                      'error':result.get('error')},ensure_ascii=False))
    return 0 if result['analysis_complete'] else 1

if __name__=='__main__':raise SystemExit(main())
