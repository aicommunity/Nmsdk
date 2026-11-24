"""Apply the documented recognition threshold to generated frozen profiles."""
import json,sys,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,CONFIG,OUT,param,save
from legacy_recover import fingerprint
def main():
    jobs=json.loads((CONFIG/'recovered-jobs.json').read_text(encoding='utf8'))
    for job in jobs:
        folder=(ROOT/job['config']).parent
        for name in ['Model_00.xml','Parameters_00.xml']:
            p=folder/name;root=ET.parse(p).getroot();subject=root.find('Model/Components/Subject')
            fixed=subject.findtext('Parameters/FixedLTZThreshold')
            param(subject,'LTZThreshold',fixed,'double')
            param(subject.find('Components/Neuron/Components/LTZone'),'Threshold',fixed,'double')
            ET.indent(root,space='\t');ET.ElementTree(root).write(p,encoding='utf8')
        job['physical_sha256']=fingerprint(ET.parse(folder/'Model_00.xml').getroot())
        job['recognition_threshold_source']='FixedLTZThreshold in archived donor; set explicitly before load'
    save(CONFIG/'recovered-jobs.json',jobs)
    print('Finalized recognition profiles',len(jobs))
if __name__=='__main__':main()
