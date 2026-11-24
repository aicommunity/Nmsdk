"""Use one reference inference engine for trained one-factor states and observe LTZone."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import inference,WORK,save
def main():
 inference('V1C','pilot',backend='VB',self_only=True,workers=1)
 for variant in ['FS','FD','FR','FO']:
  inference(variant,'factor',backend='VB',self_only=True,workers=1)
  inference(variant,'factor',workers=2)
 save(WORK/'factor-inference-completion.json',{'completed':True,'baseline_own_cases':27,'isolated_variants':['FS','FD','FR','FO'],'common_reference':'ClassicSavedStateCheck-reference.exe','zone_observer':'VB'})
if __name__=='__main__':main()
