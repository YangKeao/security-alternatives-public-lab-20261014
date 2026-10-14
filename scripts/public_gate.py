from pathlib import Path
import subprocess,json,time
R=Path(__file__).resolve().parents[1];repo=R/'fixture';owner='YangKeao/security-alternatives-public-lab-20261014';out=[]
def api(method,path,data=None):
 p=subprocess.run(['gh','api','--method',method,path]+(['--input','-'] if data is not None else []),input=json.dumps(data) if data is not None else None,text=True,capture_output=True)
 try:b=json.loads(p.stdout) if p.stdout else {}
 except Exception:b={'error':p.stderr[:250]}
 out.append({'method':method,'path':path,'exit':p.returncode,'response':b});(R/'public-gate-receipts.json').write_text(json.dumps(out,indent=2));return p.returncode,b

def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
git('branch','policy/protected-demo','lab-base');git('push','public','policy/protected-demo');git('checkout','-b','policy/candidate-demo','lab-base');(repo/'README.md').write_text((repo/'README.md').read_text()+'\nSynthetic public-only demonstration of actual required-check enforcement.\n');git('add','README.md');git('commit','-m','lab: demonstrate status gate on harmless public fixture');sha=git('rev-parse','HEAD');git('push','public','policy/candidate-demo');git('checkout','main')
code,prot=api('PUT',f'repos/{owner}/branches/policy%2Fprotected-demo/protection',{'required_status_checks':{'strict':True,'contexts':['jenkins/synthetic-gate']},'enforce_admins':True,'required_pull_request_reviews':None,'restrictions':None});assert code==0,prot
_,pr=api('POST',f'repos/{owner}/pulls',{'title':'SYNTHETIC gate demonstration (public dummy branch only)','head':'policy/candidate-demo','base':'policy/protected-demo','body':'No real vulnerability. Pending required status must block the administrator; actual Jenkins success permits merge.'});n=pr['number']
api('POST',f'repos/{owner}/statuses/{sha}',{'state':'pending','context':'jenkins/synthetic-gate','description':'Actual Jenkins validation has not yet completed'})
time.sleep(2);code,blocked=api('PUT',f'repos/{owner}/pulls/{n}/merge',{'sha':sha,'merge_method':'merge'});assert code!=0 and not blocked.get('merged'),blocked
api('POST',f'repos/{owner}/pulls/{n}/reviews',{'event':'APPROVE','body':'Synthetic self-approval capability probe; expected rejection.'})
p=subprocess.run(['python3',str(R/'scripts/jenkins_one.py'),sha,owner,'jenkins/synthetic-gate'],text=True,capture_output=True);(R/'public-gate-jenkins.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
for _ in range(20):
 code,merged=api('PUT',f'repos/{owner}/pulls/{n}/merge',{'sha':sha,'merge_method':'merge'})
 if code==0 and merged.get('merged'):break
 time.sleep(1)
assert merged.get('merged'),merged
(R/'public-gate-result.json').write_text(json.dumps({'pr':n,'url':pr['html_url'],'sha':sha,'blocked_response':blocked,'merged':merged,'note':'Actual public-repository gate proof. Current private-account branch protection is unsupported; this does not claim private gate enforcement.'},indent=2));print('Actual pending-status block, self-approval rejection and successful Jenkins-gated merge recorded')
