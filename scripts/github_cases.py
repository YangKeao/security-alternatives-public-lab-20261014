import subprocess,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'fixture';owner='YangKeao/security-embargo-private-lab-20261014';receipts=[]
def gh(method,path,data=None):
 args=['gh','api','--method',method,path]
 if data is not None:args+=['--input','-']
 p=subprocess.run(args,input=json.dumps(data) if data is not None else None,text=True,capture_output=True)
 try:out=json.loads(p.stdout)
 except Exception:out={'output':p.stdout,'error':p.stderr[:500]}
 receipts.append({'method':method,'path':path,'exit':p.returncode,'response':out});return out

def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
issues=[];prs=[]
for label in ['case:LAB-A','case:LAB-B','state:triaged','state:verified','embargo:synthetic']:
 gh('POST',f'repos/{owner}/labels',{'name':label,'color':'0052cc'})
for code,title in [('A','LAB-A: synthetic tenant boundary case'),('B','LAB-B: synthetic resource-bound case')]:
 issue=gh('POST',f'repos/{owner}/issues',{'title':title,'body':'Synthetic fixture only. Intake -> validate -> fix -> verify -> release. No real CVE. Owner: repository maintainer.','labels':[f'case:LAB-{code}','state:triaged','embargo:synthetic']});issues.append(issue)
 gh('POST',f'repos/{owner}/issues/{issue["number"]}/comments',{'body':'Triage confirmed in controlled lab. Release lines main, 8.5, 8.1; two cases will be integrated together.'})
 git('checkout','-b',f'fix/LAB-{code}','lab-base')
 if code=='A':
  (repo/'policy.py').write_text('# Synthetic LAB-A fixture.\ndef same_tenant(actor, record):\n    return actor == record\n')
  (repo/'tests/test_case_a.py').write_text('import unittest\nfrom policy import same_tenant\nclass CaseA(unittest.TestCase):\n    def test_cross_tenant_rejected(self): self.assertFalse(same_tenant("demo-a", "demo-b"))\n')
 else:
  (repo/'batch.py').write_text('# Synthetic LAB-B fixture.\ndef valid_batch(n):\n    return 0 < n <= 100\n')
  (repo/'tests/test_case_b.py').write_text('import unittest\nfrom batch import valid_batch\nclass CaseB(unittest.TestCase):\n    def test_oversized_rejected(self): self.assertFalse(valid_batch(101))\n    def test_boundary(self): self.assertTrue(valid_batch(100))\n')
 git('add','.');git('commit','-m',f'lab: fix synthetic LAB-{code} with regression');sha=git('rev-parse','HEAD');git('push','private',f'fix/LAB-{code}')
 pr=gh('POST',f'repos/{owner}/pulls',{'title':f'LAB-{code}: independent private fix','head':f'fix/LAB-{code}','base':'main','body':f'Closes #{issue["number"]}. Synthetic only; validate before merge; preserve main and LTS coverage.'});prs.append({'code':code,'sha':sha,'pr':pr})
# Lifecycle accept/edit/close/reopen is exercised on a separate synthetic intake item.
x=gh('POST',f'repos/{owner}/issues',{'title':'LAB-REJECT: synthetic duplicate report','body':'Lifecycle demonstration; contains no real security details.'});n=x['number'];gh('PATCH',f'repos/{owner}/issues/{n}',{'state':'closed','state_reason':'not_planned'});gh('PATCH',f'repos/{owner}/issues/{n}',{'state':'open'});gh('PATCH',f'repos/{owner}/issues/{n}',{'state':'closed','state_reason':'completed'})
# Branch restrictions are tested, not assumed to exist on this account/plan.
gh('PUT',f'repos/{owner}/branches/main/protection',{'required_status_checks':{'strict':True,'contexts':['jenkins/synthetic-regression']},'enforce_admins':True,'required_pull_request_reviews':None,'restrictions':None})
# A plain status write is impossible on GSA temporary forks but available here.
for x in prs:gh('POST',f'repos/{owner}/statuses/{x["sha"]}',{'state':'pending','context':'jenkins/synthetic-regression','description':'Waiting for isolated Jenkins execution'})
git('checkout','main')
(R/'github-cases.json').write_text(json.dumps({'issues':[{'number':x['number'],'url':x['html_url']} for x in issues],'fixes':prs},indent=2))
(R/'github-api-receipts.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2))
print('Created retained private cases/PRs and status/protection probes')
