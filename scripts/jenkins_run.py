from pathlib import Path
import requests,json,time,subprocess
R=Path(__file__).resolve().parents[1];auth=json.load(open(R/'.secrets/lab-auth.json'));s=requests.Session();s.trust_env=False;s.auth=('labadmin',auth['jenkins_admin_password']);base='http://127.0.0.1:18981';c=s.get(base+'/crumbIssuer/api/json').json();s.headers[c['crumbRequestField']]=c['crumb'];out=[]
fixes=json.load(open(R/'github-cases.json'))['fixes'];repo=R/'fixture'
def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
git('checkout','-b','test/LAB-A-before-fix','lab-base');(repo/'tests/test_case_a.py').write_text('import unittest\nfrom policy import same_tenant\nclass CaseA(unittest.TestCase):\n    def test_cross_tenant_rejected(self): self.assertFalse(same_tenant("demo-a", "demo-b"))\n');git('add','.');git('commit','-m','lab: prove regression before fix');bad=git('rev-parse','HEAD');git('push','private','test/LAB-A-before-fix');git('checkout','main')
for label,sha,expected in [('regression-before-fix',bad,'FAILURE')]+[(x['code'],x['sha'],'SUCCESS') for x in fixes]:
 r=s.post(base+'/job/synthetic-embargo/buildWithParameters',params={'SHA':sha});r.raise_for_status();queue=r.headers['Location'];num=None
 for _ in range(120):
  q=s.get(queue+'api/json').json()
  if q.get('executable'):num=q['executable']['number'];break
  time.sleep(.5)
 assert num is not None
 url=f'{base}/job/synthetic-embargo/{num}/'
 for _ in range(120):
  b=s.get(url+'api/json').json()
  if not b['building']:break
  time.sleep(.5)
 log=s.get(url+'consoleText').text;(R/f'jenkins-build-{num}.log').write_text(log)
 record={'label':label,'sha':sha,'build':num,'result':b['result'],'url':url,'expected':expected};out.append(record)
 print(label,b['result'],num,flush=True);assert b['result']==expected,log[-800:]
 data={'state':'success' if b['result']=='SUCCESS' else 'failure','context':'jenkins/synthetic-regression','target_url':url,'description':f'Isolated Jenkins actual build #{num}: {b["result"]}'}
 p=subprocess.run(['gh','api','--method','POST',f'repos/YangKeao/security-embargo-private-lab-20261014/statuses/{sha}','--input','-'],input=json.dumps(data),capture_output=True,text=True);assert p.returncode==0,p.stderr;record['github_status_id']=json.loads(p.stdout)['id']
(R/'jenkins-builds.json').write_text(json.dumps(out,indent=2))
