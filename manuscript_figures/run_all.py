from pathlib import Path
import argparse,json,subprocess,sys,os
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--figures',nargs='*',type=int)
args=parser.parse_args()
manifest=json.loads((ROOT/'figure_manifest.json').read_text(encoding='utf-8'))
results=[]
for item in manifest:
    if args.figures and item['figure'] not in args.figures: continue
    if not item.get('script'):
        results.append({'figure':item['figure'],'status':'no_script'})
        continue
    env=os.environ.copy();env['MPLBACKEND']='Agg';env['PYTHONDONTWRITEBYTECODE']='1'
    result=subprocess.run([sys.executable,str(ROOT/item['script'])],cwd=ROOT,env=env,capture_output=True)
    status='passed' if result.returncode==0 else 'failed'
    results.append({'figure':item['figure'],'status':status,'exit_code':result.returncode})
    print('Fig.',item['figure'],status,flush=True)
print(json.dumps(results, indent=2))
sys.exit(1 if any(r['status']=='failed' for r in results) else 0)
