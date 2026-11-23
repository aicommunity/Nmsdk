"""Find native snapshot serialization failures; preserve failed attempts before replay."""
import argparse,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import OUT,save

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preserve',action='store_true');a=parser.parse_args()
    failures=[];checked=0
    for stage in ['saved-b','recovered-b','protocols-a','context-a','initialization-a']:
        for folder in sorted((OUT/stage).glob('*')):
            if not (folder/'process.json').exists():continue
            process=json.loads((folder/'process.json').read_text(encoding='utf8'))
            if process['status']=='running':continue
            errors=[]
            if process['status']!='completed':errors.append('process status '+process['status'])
            try:
                manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'));job=manifest['legacy_job']
                # The initial saved-b binary predates the separate roundtrip
                # XML snapshot. Nine later reload-first controls cover it.
                roundtrip=job.get('roundtrip') and (stage!='saved-b' or (folder/'roundtrip-loaded').exists())
                snapshots=['loaded'] if job.get('audit_only') else ['loaded','after']+(['roundtrip-loaded'] if roundtrip else [])
                for snapshot in snapshots:
                    for name in ['Model_00.xml','Parameters_00.xml']:
                        try:ET.parse(folder/snapshot/name)
                        except (OSError,ET.ParseError) as e:errors.append(snapshot+'/'+name+': '+str(e))
                log=(folder/'stderr.log').read_text(encoding='utf8',errors='replace')
                if "Can't save model file" in log or "Can't save parameters file" in log:errors.append('native serialization error in stderr')
            except (OSError,ValueError) as e:errors.append(str(e))
            checked+=1
            if errors:
                failures.append({'stage':stage,'case':folder.name,'errors':errors})
                if a.preserve:
                    target=OUT/'preserved-incomplete-attempts'/stage/folder.name
                    if not folder.resolve().is_relative_to(OUT.resolve()) or not target.resolve().is_relative_to(OUT.resolve()):raise ValueError('Unsafe preservation path')
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if target.exists():raise ValueError('Refusing to replace preserved attempt '+str(target))
                    folder.rename(target)
    result={'checked':checked,'failures':failures,'preserved':a.preserve}
    save(OUT/('snapshot-preservation.json' if a.preserve else 'snapshot-audit.json'),result)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
