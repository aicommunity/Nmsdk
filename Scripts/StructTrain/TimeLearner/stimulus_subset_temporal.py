"""Readable temporal reports for audited Console subset diagnostics; render on workers."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re

from .native_characterization import audit_execution
from .native_evidence import load, number, require


def render(corpus, output, evidence_commit):
    require(type(evidence_commit) is str and re.fullmatch('[0-9a-f]{40}', evidence_commit),
            'subset_report_requires_declared_git_evidence')
    corpus,output = Path(corpus).resolve(strict=True),Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(corpus) and not corpus.is_relative_to(output),
            'subset_report_output_overlaps_primary')
    cases=[];limits={};bindings={}
    for name in load(corpus/'index.json')['native_directories']:
        require(type(name) is str and '\\' not in name and ':' not in name and
                not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts,
                'subset_report_invalid_case_path')
        folder=corpus/name;require(folder.resolve(strict=True).is_relative_to(corpus),'subset_report_case_alias')
        audit=audit_execution(folder);require(audit['execution']=='completed','subset_report_requires_closed_diagnostic')
        quality=audit['stimulus_subset_diagnostic'];job=load(folder/'job.json')
        packet=load(folder/'probe_trial_1.json');spec=packet['observation']['specification']
        with (folder/'probe_trial_1.csv').open(newline='',encoding='utf-8') as stream:rows=list(csv.reader(stream))
        samples=[[number(float(value)) for value in row] for row in rows[1:]]
        key='Branch' if job['model']['branch'] else 'Classic';potentials=[value for row in samples for value in row[2:]]
        lo,hi=min(potentials+spec['baseline']),max(potentials+spec['baseline'])
        old=limits.get(key,(lo,hi));limits[key]=(min(lo,old[0]),max(hi,old[1]))
        for filename in ['job.json','execution.json','probe_trial_1.json','probe_trial_1.csv','subset-restoration.json']:
            raw=(folder/filename).read_bytes();bindings[name+'/'+filename]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        cases.append((name,key,quality,spec,samples,packet['observation']['stimuli']))
    require(bool(cases),'subset_report_empty_corpus')
    # Import/render only after validation. No work runs at module import.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':12,'axes.titlesize':12,'axes.labelsize':12,'xtick.labelsize':11,'ytick.labelsize':11})
    output.mkdir(parents=True,exist_ok=False);figures=[]
    for serial,(name,key,quality,spec,samples,events) in enumerate(cases,1):
        begin=spec['begin'];times=[row[0]-begin for row in samples];channels=quality['channel_count']
        source=[row[1] for row in samples];event_times=[event['time']-begin for event in events]
        active=[i for i,row in enumerate(samples) if any(abs(value-spec['baseline'][c])>spec['minimum_amplitude']
                                                       for c,value in enumerate(row[2:]))]
        dt=1/quality['frequency_hz'];onset=min(event_times)
        last=max(event_times+([times[active[-1]]] if active else []))
        views={'overview':(times[0],times[-1]),'response':(max(times[0],min(onset,times[active[0]] if active else onset)-20*dt),
                                                                    min(times[-1],last+40*dt))}
        for view,bounds in views.items():
            fig,axes=plt.subplots(channels+1,1,figsize=(16,3.6*(channels+1)),sharex=True,layout='constrained')
            fig.suptitle(key+' | retained source ordinals '+str(quality['source_ordinals'])+' | '+view+'\n'
                         'Frozen diagnostic; no peak assignment or classification verdict\n'
                         'Model '+quality['model_revision'][:16]+' | native potential units; SI unverified',fontsize=13)
            axes[0].step(times,source,where='post',color='#ed8a28',linewidth=1.2,label='Recorded native generator output')
            for event,time in zip(events,event_times):
                axes[0].axvline(time,color='gray',linestyle=':',linewidth=.9)
                axes[0].annotate(event['id'],(time,spec['stimulus_profile']['amplitude']),xytext=(3,5),textcoords='offset points',fontsize=10)
            axes[0].set_ylabel('Native input units');axes[0].legend(loc='upper right',fontsize=10)
            lo,hi=limits[key];pad=max((hi-lo)*.08,1e-12)
            for c,axis in enumerate(axes[1:]):
                axis.plot(times,[row[c+2] for row in samples],color='#205bb1',linewidth=1.4,label='Raw soma potential')
                axis.axhline(spec['baseline'][c],color='gray',linewidth=.7,linestyle='--',label='Declared rest baseline')
                overlay=axis.twinx();overlay.step(times,source,where='post',color='#ed8a28',alpha=.35,linewidth=.8)
                overlay.set_ylim(-.05*spec['stimulus_profile']['amplitude'],1.1*spec['stimulus_profile']['amplitude'])
                overlay.set_ylabel('Native input',color='#9c6028',fontsize=10);overlay.tick_params(axis='y',labelsize=9)
                for time in event_times:axis.axvline(time,color='gray',linestyle=':',linewidth=.7)
                axis.set_ylim(lo-pad,hi+pad);axis.set_ylabel('Native potential');axis.set_title('Soma '+str(c+1));axis.grid(alpha=.2)
            axes[-1].set_xlabel('Time relative to actual observation start [s]');axes[-1].set_xlim(*bounds)
            stem=f'{serial:02d}-{key}-{view}'
            for suffix in ('png','svg'):fig.savefig(output/(stem+'.'+suffix),dpi=140)
            plt.close(fig);figures.append({'case':name,'view':view,'png':stem+'.png','svg':stem+'.svg','x_bounds_s':bounds,
                                         'pixels':[2240,round(140*3.6*(channels+1))]})
    records={path.name:{'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
             for path in output.iterdir() if path.is_file()}
    manifest={'kind':'stimulus_subset_temporal_report','schema_version':1,'declared_source_evidence':evidence_commit,
              'primary_file_bindings':bindings,'figures':figures,'figure_files':records,'cases':len(cases),
              'y_scale':'shared across cases and soma panels within each topology','spike_response':'unknown',
              'peak_assignment':'not_performed','scientific_verdict':None}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    entries='\n'.join('<h2>'+html.escape(row['case']+' / '+row['view'])+'</h2><a href="'+row['svg']+'">SVG</a><br><img style="width:100%;max-width:2240px" src="'+row['png']+'">' for row in figures)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Native subset waveforms</title>'
        '<h1>Frozen native subset diagnostics</h1><p>All recorded soma channels, actual input overlay and event timestamps. '
        'Open SVG for detailed scaling. No training or classification verdict.</p>'+entries,encoding='utf-8')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--corpus',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--source-evidence',required=True)
    args=parser.parse_args();result=render(args.corpus,args.output,args.source_evidence)
    print(json.dumps({'cases':result['cases'],'figures':len(result['figures'])}))


if __name__=='__main__':main()
