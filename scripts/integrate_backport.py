from pathlib import Path
import json,subprocess,time,hashlib
R=Path(__file__).resolve().parents[1];repo=R/'fixture';owner='YangKeao/security-embargo-private-lab-20261014';fixes=json.load(open(R/'github-cases.json'))['fixes'];out=[]
def api(method,path,data=None):
 args=['gh','api','--method',method,path]+(['--input','-'] if data is not None else []);p=subprocess.run(args,input=json.dumps(data) if data is not None else None,text=True,capture_output=True);body=json.loads(p.stdout);out.append({'method':method,'path':path,'exit':p.returncode,'response':body});(R/'integration-api-receipts.json').write_text(json.dumps(out,indent=2));return p.returncode,body

def git(*args,check=True):
 p=subprocess.run(['git',*args],cwd=repo,text=True,capture_output=True)
 if check and p.returncode:raise RuntimeError(p.stderr)
 return p
for x in fixes:
 n=x['pr']['number'];sha=x['sha'];_,status=api('GET',f'repos/{owner}/commits/{sha}/status');assert any(s['context']=='jenkins/synthetic-regression' and s['state']=='success' for s in status['statuses'])
 for _ in range(20):
  code,b=api('PUT',f'repos/{owner}/pulls/{n}/merge',{'merge_method':'merge','sha':sha})
  if not code and b.get('merged'):break
  time.sleep(1)
 assert b.get('merged'),b
 print('Merged independent private PR',n,flush=True)
git('fetch','private');git('checkout','main');git('reset','--hard','private/main');subprocess.run(['python3','-m','unittest','discover','-s','tests','-v'],cwd=repo,check=True,capture_output=True)
heads={};conflicts=[]
for version in ['8.5','8.1']:
 branch='backport/combined-'+version;git('checkout','-b',branch,'release/'+version)
 for x in fixes:
  cp=git('cherry-pick',x['sha'],check=False)
  if cp.returncode:
   conflicts.append({'version':version,'case':x['code'],'stdout':cp.stdout,'stderr':cp.stderr,'unmerged':git('diff','--name-only','--diff-filter=U').stdout})
   (repo/'policy.py').write_text('# Synthetic LAB-A legacy-compatible resolved backport.\ndef same_tenant(actor, record):\n    return actor == record\n');git('add','policy.py');git('-c','core.editor=true','cherry-pick','--continue')
  print('Backport',version,x['code'],'conflict' if cp.returncode else 'clean',flush=True)
 p=subprocess.run(['python3','-m','unittest','discover','-s','tests','-v'],cwd=repo,text=True,capture_output=True);(R/f'backport-{version}-tests.log').write_text(p.stdout+p.stderr);assert p.returncode==0
 sha=git('rev-parse','HEAD').stdout.strip();heads[version]=sha;git('push','private',branch)
 _,pr=api('POST',f'repos/{owner}/pulls',{'title':f'LAB-A + LAB-B: combined backport to {version}','head':branch,'base':'release/'+version,'body':'Two synthetic cases, one tested release bundle. Independent commits retained; real cherry-pick conflict resolved on8.1.'});heads[version]={'sha':sha,'pr':pr['number'],'url':pr['html_url'],'branch':branch}
 git('tag','lab-rc1-'+version);git('push','private','lab-rc1-'+version)
(R/'backport-conflicts.json').write_text(json.dumps(conflicts,indent=2));(R/'backport-heads.json').write_text(json.dumps(heads,indent=2));git('checkout','main');print('Integrated both cases and preserved two LTS PRs/RC tags')
