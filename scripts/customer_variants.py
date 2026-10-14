from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[1];repo=R/'fixture';out=R/'manual';variants=[]
def git(*a,cwd=repo):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
base=json.load(open(R/'backport-heads.json'))['8.5']['sha']
for name in ['demo-a','demo-b']:
 git('checkout','-b','lab/customer-'+name,base);(repo/'CUSTOMER.txt').write_text('Synthetic customer variant '+name+'\n');git('add','CUSTOMER.txt');git('commit','-m','lab: synthetic customer patch '+name);sha=git('rev-parse','HEAD');tree=git('rev-parse','HEAD^{tree}');patch=out/('customer-'+name+'.patch');patch.write_text(git('format-patch','-1',sha,'--stdout'));git('push','private','lab/customer-'+name)
 rebuilt=R/('rebuilt-customer-'+name);subprocess.run(['git','clone',str(out/'decrypted.gitbundle'),str(rebuilt)],check=True,capture_output=True);git('checkout','-b','rebuild','lab-rc1-8.5',cwd=rebuilt);git('config','user.name','Synthetic rebuilder',cwd=rebuilt);git('config','user.email','rebuilder@example.invalid',cwd=rebuilt);git('am',str(patch),cwd=rebuilt);actual_tree=git('rev-parse','HEAD^{tree}',cwd=rebuilt);assert actual_tree==tree
 p=subprocess.run(['python3','-m','unittest','discover','-s','tests','-v'],cwd=rebuilt,text=True,capture_output=True);(out/('customer-'+name+'-tests.log')).write_text(p.stdout+p.stderr);assert p.returncode==0
 variants.append({'variant':name,'base_commit':base,'already_in_base':['LAB-A','LAB-B'],'patch_order':[{'file':patch.name,'canonical_commit':sha,'sha256':hashlib.sha256(patch.read_bytes()).hexdigest()}],'expected_tree':tree,'rebuilt_tree_matches':True,'regression_exit':p.returncode})
git('checkout','main');manifest=out/'customer-variants-manifest.json';manifest.write_text(json.dumps({'synthetic':True,'variants':variants},indent=2));subprocess.run(['gpg','--homedir',str(R/'.secrets/gpg-maintainer'),'--batch','--armor','--detach-sign',str(manifest)],check=True,capture_output=True)
files=[str(manifest),str(manifest)+'.asc',str(out/'customer-demo-a.patch'),str(out/'customer-demo-b.patch')]
for repo_name,tag in [('security-embargo-private-lab-20261014','lab-private-rc1'),('security-alternatives-public-lab-20261014','lab-public-rc1-8.5')]:subprocess.run(['gh','release','upload',tag,'--repo','YangKeao/'+repo_name,*files],check=True,capture_output=True)
(R/'customer-variant-results.json').write_text(json.dumps(variants,indent=2));print('Two customer variants reconstructed offline from shared RC+ordered patch manifests; matching source trees and regressions passed')
