from pathlib import Path
import json,subprocess,hashlib,requests
R=Path(__file__).resolve().parents[1];m=R/'manual';private='YangKeao/security-embargo-private-lab-20261014';public='YangKeao/security-alternatives-public-lab-20261014';tag='lab-private-rc1';notes=R/'release-notes.txt';notes.write_text('SYNTHETIC ONLY: LAB-A/LAB-B, not a CVE and not a real vulnerability disclosure. Two tested LTS artifacts, encrypted offline bundle, signed release manifest. No production data or human credentials.\n')
files=[m/'release-bundle.gitbundle.gpg',m/'release-manifest.json',m/'release-manifest.json.asc',m/'maintainer-public.asc',m/'lab-rc1-8.5.tar',m/'lab-rc1-8.1.tar']
p=subprocess.run(['gh','release','create',tag,'--repo',private,'--target','main','--prerelease','--title','[SYNTHETIC] Private RC1','--notes-file',str(notes),*[str(x) for x in files]],text=True,capture_output=True);assert p.returncode==0,p.stderr
meta=json.loads(subprocess.check_output(['gh','api',f'repos/{private}/releases/tags/{tag}'],text=True));(R/'private-release.json').write_text(json.dumps(meta,indent=2));print('Private synthetic candidate',meta['html_url'],flush=True)
# Actual candidate download, followed by digest verification.
download=R/'private-release-download';download.mkdir(exist_ok=True);subprocess.run(['gh','release','download',tag,'--repo',private,'--dir',str(download)],check=True,capture_output=True)
records=[]
for x in files:
 got=download/x.name;assert got.read_bytes()==x.read_bytes();u=next(a['browser_download_url'] for a in meta['assets'] if a['name']==x.name);anon=requests.get(u,allow_redirects=False,timeout=30);records.append({'asset':x.name,'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'authenticated_download_matches':True,'anonymous_http':anon.status_code})
# A public tag preserves the exact tested commit; assets are promoted, never rebuilt.
heads=json.load(open(R/'backport-heads.json'));git=R/'fixture'
for v,h in heads.items():subprocess.run(['git','push','public',f'{h["sha"]}:refs/tags/lab-public-rc1-{v}'],cwd=git,check=True,capture_output=True)
pubtag='lab-public-rc1-8.5';p=subprocess.run(['gh','release','create',pubtag,'--repo',public,'--prerelease','--title','[SYNTHETIC] Public promotion rehearsal','--notes-file',str(notes),*[str(download/x.name) for x in files]],capture_output=True,text=True);assert p.returncode==0,p.stderr
pub=json.loads(subprocess.check_output(['gh','api',f'repos/{public}/releases/tags/{pubtag}'],text=True));(R/'public-release.json').write_text(json.dumps(pub,indent=2));dest=R/'public-release-download';dest.mkdir(exist_ok=True);subprocess.run(['gh','release','download',pubtag,'--repo',public,'--dir',str(dest)],check=True,capture_output=True)
for record in records:
 p=dest/record['asset'];record['public_promotion_hash_matches']=hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'];assert record['public_promotion_hash_matches']
(R/'release-promotion-results.json').write_text(json.dumps(records,indent=2));print('All six private downloaded assets promoted byte-for-byte to synthetic public release')
