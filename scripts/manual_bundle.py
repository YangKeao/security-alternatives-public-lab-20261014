from pathlib import Path
import subprocess,json,hashlib,os,shutil
R=Path(__file__).resolve().parents[1];repo=R/'fixture';out=R/'manual';out.mkdir(exist_ok=True);heads=json.load(open(R/'backport-heads.json'));fixes=json.load(open(R/'github-cases.json'))['fixes'];result={}
def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
# Each role has its own private keyring, all locally generated synthetic keys.
for role,usage in [('maintainer','sign'),('downstream','encrypt'),('stranger','encrypt')]:
 home=R/'.secrets'/('gpg-'+role);home.mkdir(mode=0o700,exist_ok=True)
 existing=subprocess.run(['gpg','--homedir',str(home),'--with-colons','--list-keys'],capture_output=True,text=True)
 if 'fpr:' not in existing.stdout:
  p=subprocess.run(['gpg','--homedir',str(home),'--batch','--pinentry-mode','loopback','--passphrase','','--quick-generate-key',f'Synthetic {role} <{role}@example.invalid>','ed25519' if usage=='sign' else 'rsa3072',usage,'7d'],capture_output=True,text=True);assert p.returncode==0,p.stderr
 key=subprocess.check_output(['gpg','--homedir',str(home),'--with-colons','--list-keys'],text=True,stderr=subprocess.DEVNULL);fpr=next(l.split(':')[9] for l in key.splitlines() if l.startswith('fpr:'));result[role]={'fingerprint':fpr}
 public=subprocess.check_output(['gpg','--homedir',str(home),'--armor','--export',fpr]);(out/(role+'-public.asc')).write_bytes(public)
# Offline bundle, separate fix patches, and precise source/artifact hashes.
bundle=out/'release-bundle.gitbundle';git('bundle','create',str(bundle),'lab-rc1-8.5','lab-rc1-8.1','lab-base');(out/'bundle-verify.txt').write_text(git('bundle','verify',str(bundle)))
artifacts={}
for version,head in heads.items():
 tar=subprocess.check_output(['git','archive','--format=tar',head['sha']],cwd=repo);path=out/f'lab-rc1-{version}.tar';path.write_bytes(tar);artifacts[version]={'sha':head['sha'],'artifact':path.name,'sha256':hashlib.sha256(tar).hexdigest()}
for x in fixes:(out/f'LAB-{x["code"]}.patch').write_text(git('format-patch','-1',x['sha'],'--stdout'))
manifest={'synthetic':True,'not_a_cve':True,'base':git('rev-parse','lab-base'),'cases':[{'id':'LAB-'+x['code'],'canonical_commit':x['sha']} for x in fixes],'release_lines':artifacts,'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'conflicts':json.load(open(R/'backport-conflicts.json'))}
path=out/'release-manifest.json';path.write_text(json.dumps(manifest,indent=2))
maint=R/'.secrets/gpg-maintainer';down=R/'.secrets/gpg-downstream';other=R/'.secrets/gpg-stranger'
subprocess.run(['gpg','--homedir',str(maint),'--batch','--import',str(out/'downstream-public.asc')],check=True,capture_output=True)
subprocess.run(['gpg','--homedir',str(maint),'--batch','--armor','--detach-sign',str(path)],check=True,capture_output=True)
subprocess.run(['gpg','--homedir',str(maint),'--batch','--trust-model','always','--recipient',result['downstream']['fingerprint'],'--output',str(out/'release-bundle.gitbundle.gpg'),'--encrypt',str(bundle)],check=True,capture_output=True)
subprocess.run(['gpg','--homedir',str(down),'--batch','--import',str(out/'maintainer-public.asc')],check=True,capture_output=True)
verify=subprocess.run(['gpg','--homedir',str(down),'--verify',str(path)+'.asc',str(path)],capture_output=True,text=True);result['signature_verify_exit']=verify.returncode;(out/'signature-verify.txt').write_text(verify.stderr);assert verify.returncode==0
wrong=subprocess.run(['gpg','--homedir',str(other),'--batch','--output',str(out/'wrong-recipient-output'),'--decrypt',str(out/'release-bundle.gitbundle.gpg')],capture_output=True,text=True);result['wrong_recipient_exit']=wrong.returncode;(out/'wrong-recipient.txt').write_text(wrong.stderr);assert wrong.returncode!=0
plain=out/'decrypted.gitbundle';ok=subprocess.run(['gpg','--homedir',str(down),'--batch','--output',str(plain),'--decrypt',str(out/'release-bundle.gitbundle.gpg')],capture_output=True,text=True);assert ok.returncode==0;result['bundle_hash_matches']=hashlib.sha256(plain.read_bytes()).hexdigest()==manifest['bundle_sha256'];assert result['bundle_hash_matches']
clone=R/'manual-downstream';subprocess.run(['git','clone',str(plain),str(clone)],check=True,capture_output=True)
for version in heads:
 subprocess.run(['git','checkout','lab-rc1-'+version],cwd=clone,check=True,capture_output=True);test=subprocess.run(['python3','-m','unittest','discover','-s','tests','-v'],cwd=clone,capture_output=True,text=True);(out/f'downstream-{version}-tests.txt').write_text(test.stdout+test.stderr);assert test.returncode==0
# Tampered manifest must not verify.
tampered=out/'release-manifest-tampered.json';tampered.write_bytes(path.read_bytes()+b' ');bad=subprocess.run(['gpg','--homedir',str(down),'--verify',str(path)+'.asc',str(tampered)],capture_output=True,text=True);result['tampered_signature_exit']=bad.returncode;(out/'tampered-signature.txt').write_text(bad.stderr);assert bad.returncode!=0
(R/'manual-results.json').write_text(json.dumps(result,indent=2));print('Manual encrypted handoff: correct key success; wrong key rejected; signature/tamper/hash checks and both offline LTS regressions passed')
