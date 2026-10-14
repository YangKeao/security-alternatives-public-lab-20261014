from pathlib import Path
import json,re,subprocess,requests
R=Path(__file__).resolve().parents[1];text=(R/'cloudflared-http2.log').read_text();matches=re.findall(r'https://[a-z0-9-]+\.trycloudflare\.com',text);assert matches,'tunnel URL not available';url=matches[0];r=requests.get(url+'/health',timeout=30);assert r.status_code==200,(r.status_code,r.text[:200]);auth=json.load(open(R/'.secrets/lab-auth.json'))
data={'name':'web','active':True,'events':['push'],'config':{'url':url+'/hook/github','content_type':'json','secret':auth['webhook_secret'],'insecure_ssl':'0'}}
p=subprocess.run(['gh','api','--method','POST','repos/YangKeao/security-embargo-private-lab-20261014/hooks','--input','-'],input=json.dumps(data),text=True,capture_output=True);assert p.returncode==0,p.stderr;hook=json.loads(p.stdout);hook.get('config',{}).pop('secret',None);(R/'github-hook.json').write_text(json.dumps(hook,indent=2))
repo=R/'fixture'
def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
git('checkout','-b','ci/webhook-github','backport/combined-8.5');(repo/'README.md').write_text((repo/'README.md').read_text()+'\nActual GitHub push -> signed webhook -> isolated Jenkins -> GitHub status.\n');git('add','README.md');git('commit','-m','lab: real private GitHub webhook exercise');sha=git('rev-parse','HEAD');git('push','private','ci/webhook-github');git('checkout','main');(R/'github-webhook-trigger.json').write_text(json.dumps({'hook_id':hook['id'],'url':url,'sha':sha},indent=2));print('Registered actual GitHub hook and pushed CI trigger')
