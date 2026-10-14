from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json,hmac,hashlib,re,threading,subprocess,time,requests
R=Path(__file__).resolve().parents[1];auth=json.load(open(R/'.secrets/lab-auth.json'));lock=threading.Lock();jenkins='http://127.0.0.1:18981';events=R/'webhook-events.jsonl'
def status(platform,sha,ref,state,url='',desc=''):

 data={'state':{'failed':'failure'}.get(state,state),'context':'jenkins/synthetic-regression','target_url':url,'description':desc}
 p=subprocess.run(['gh','api','--method','POST',f'repos/YangKeao/security-embargo-private-lab-20261014/statuses/{sha}','--input','-'],input=json.dumps(data),text=True,capture_output=True);return {'exit':p.returncode,'body':json.loads(p.stdout)}
def execute(platform,sha,ref):
 with lock:
  result={'platform':platform,'sha':sha,'ref':ref}
  try:
   subprocess.run(['git','fetch','private'],cwd=R/'fixture',check=True,capture_output=True)
   result['pending_status']=status(platform,sha,ref,'pending',desc='Waiting for actual isolated Jenkins build')
   s=requests.Session();s.trust_env=False;s.auth=('labadmin',auth['jenkins_admin_password']);c=s.get(jenkins+'/crumbIssuer/api/json').json();s.headers[c['crumbRequestField']]=c['crumb']
   r=s.post(jenkins+'/job/synthetic-embargo/buildWithParameters',params={'SHA':sha});r.raise_for_status();queue=r.headers['Location'];num=None
   for _ in range(120):
    q=s.get(queue+'api/json').json()
    if q.get('executable'):num=q['executable']['number'];break
    time.sleep(.5)
   assert num is not None
   url=f'{jenkins}/job/synthetic-embargo/{num}/'
   for _ in range(120):
    b=s.get(url+'api/json').json()
    if not b['building']:break
    time.sleep(.5)
   result.update(build=num,result=b['result'],url=url)
   (R/f'jenkins-build-{num}.log').write_text(s.get(url+'consoleText').text)
   result['final_status']=status(platform,sha,ref,'success' if b['result']=='SUCCESS' else 'failed',url,f'Actual Jenkins #{num}: {b["result"]}')
  except Exception as e:result['error']=str(e)[:300]
  with (R/'webhook-builds.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
  print(platform,sha[:8],result.get('result',result.get('error')),flush=True)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  self.send_response(200 if self.path=='/health' else 404);self.end_headers();self.wfile.write(b'synthetic webhook bridge')
 def do_POST(self):
  raw=self.rfile.read(int(self.headers.get('Content-Length','0')));platform=self.path.rsplit('/',1)[-1]
  if platform=='github':valid=hmac.compare_digest(self.headers.get('X-Hub-Signature-256',''),'sha256='+hmac.new(auth['webhook_secret'].encode(),raw,hashlib.sha256).hexdigest())
  else:valid=False
  if not valid:self.send_response(403);self.end_headers();return
  payload=json.loads(raw or b'{}');sha=payload.get('after','');ref=payload.get('ref','').replace('refs/heads/','');repo=payload.get('repository',{}).get('full_name')
  allowed=platform=='github' and repo=='YangKeao/security-embargo-private-lab-20261014'
  if not allowed or not re.fullmatch('[0-9a-f]{40}',sha) or sha=='0'*40:
   self.send_response(200);self.end_headers();return
  with events.open('a') as f:f.write(json.dumps({'platform':platform,'sha':sha,'ref':ref,'event':self.headers.get('X-Github-Event') or self.headers.get('X-Gitlab-Event'),'received':time.time()})+'\n')
  self.send_response(202);self.end_headers();threading.Thread(target=execute,args=(platform,sha,ref),daemon=True).start()
print('Synthetic signed webhook bridge on port18989',flush=True)
ThreadingHTTPServer(('127.0.0.1',18989),Handler).serve_forever()
