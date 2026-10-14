from pathlib import Path
import subprocess,json,re
R=Path(__file__).resolve().parents[1];owner='YangKeao/security-alternatives-public-lab-20261014';private='YangKeao/security-embargo-private-lab-20261014';out=[]
def api(method,path,data=None):
 p=subprocess.run(['gh','api','--method',method,path]+(['--input','-'] if data is not None else []),input=json.dumps(data) if data is not None else None,text=True,capture_output=True)
 try:body=json.loads(p.stdout) if p.stdout else {}
 except Exception:body={'error':p.stderr[:400]}
 out.append({'method':method,'path':path,'exit':p.returncode,'response':body});(R/'github-hybrid-receipts.json').write_text(json.dumps(out,indent=2));return p.returncode,body
api('PUT',f'repos/{owner}/private-vulnerability-reporting')
fixes=json.load(open(R/'github-cases.json'))['fixes'];drafts=[]
for x in fixes:
 description=f'''### Impact\nEntirely synthetic LAB-{x['code']}; no actual product vulnerability, CVE or affected customer.\n\n### Patches\nThis draft tracks a synthetic case while development/CI takes place in a standing private repository.\nPrivate fix PR: {x['pr']['html_url']}\nCanonical synthetic commit: {x['sha']}\n\n### Workarounds\nNo real remediation is needed.\n\n### References\nPrivate integration has two LTS backport PRs and an encrypted RC manifest. No public advisory publication is requested.\n'''
 code,a=api('POST',f'repos/{owner}/security-advisories',{'summary':f'[SYNTHETIC] LAB-{x["code"]} hybrid workflow demonstration','description':description,'severity':'low','vulnerabilities':[]});assert code==0,a
 iid=int(re.search(r'Closes #(\d+)',x['pr']['body']).group(1))
 api('POST',f'repos/{private}/issues/{iid}/comments',{'body':f'Synthetic hybrid case record: {a["ghsa_id"]}. Draft-only; no CVE requested. Development and immutable-SHA CI are retained in this ordinary private repository, not in a temporary advisory fork.'})
 drafts.append({'case':x['code'],'ghsa_id':a['ghsa_id'],'url':a['html_url'],'state':a['state'],'private_pr':x['pr']['html_url'],'sha':x['sha']})
(R/'hybrid-drafts.json').write_text(json.dumps(drafts,indent=2));print('Created two retained draft advisories linked to ordinary private case/PR/CI evidence')
