from pathlib import Path
import requests,json,time,subprocess,sys
R=Path(__file__).resolve().parents[1];sha=sys.argv[1];repo=sys.argv[2] if len(sys.argv)>2 else 'YangKeao/security-embargo-private-lab-20261014';context=sys.argv[3] if len(sys.argv)>3 else 'jenkins/synthetic-regression';assert repo in ['YangKeao/security-embargo-private-lab-20261014','YangKeao/security-alternatives-public-lab-20261014'];auth=json.load(open(R/'.secrets/lab-auth.json'));s=requests.Session();s.trust_env=False;s.auth=('labadmin',auth['jenkins_admin_password']);base='http://127.0.0.1:18981';c=s.get(base+'/crumbIssuer/api/json').json();s.headers[c['crumbRequestField']]=c['crumb'];r=s.post(base+'/job/synthetic-embargo/buildWithParameters',params={'SHA':sha});r.raise_for_status();queue=r.headers['Location'];num=None
for _ in range(120):
 q=s.get(queue+'api/json').json()
 if q.get('executable'):num=q['executable']['number'];break
 time.sleep(.5)
assert num is not None;url=f'{base}/job/synthetic-embargo/{num}/'
for _ in range(120):
 b=s.get(url+'api/json').json()
 if not b['building']:break
 time.sleep(.5)
(R/f'jenkins-build-{num}.log').write_text(s.get(url+'consoleText').text);data={'state':'success' if b['result']=='SUCCESS' else 'failure','context':context,'target_url':url,'description':f'Actual isolated Jenkins #{num}: {b["result"]}'};p=subprocess.run(['gh','api','--method','POST',f'repos/{repo}/statuses/{sha}','--input','-'],input=json.dumps(data),text=True,capture_output=True);assert p.returncode==0,p.stderr
record={'sha':sha,'repo':repo,'context':context,'build':num,'result':b['result'],'url':url,'status_id':json.loads(p.stdout)['id']};(R/f'jenkins-result-{num}.json').write_text(json.dumps(record,indent=2));print(json.dumps(record));assert b['result']=='SUCCESS'
