#!/usr/bin/env python3
"""Execute the documented installer, including multi-host and refusal controls."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];HOSTS={'cursor':'.cursor','copilot':'.github','codex':'.agents'};NAMES=('redteam','assess','pr-review')
def check(source):
 code=(ROOT/'docs/install-portable-skills.md').read_text().split('```python\n',1)[1].split('\n```',1)[0]
 def install(target,host):
  env=dict(os.environ,AI_REDTEAM_SOURCE=str(source),AI_REDTEAM_TARGET=str(target),AI_REDTEAM_HOST=host)
  return subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True)
 def tree(target):return {str(p.relative_to(target)):hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file()}
 def verify(target,host):
  result=[]
  for name in NAMES:
   path=Path(HOSTS[host])/'skills'/name/'SKILL.md';data=(target/path).read_bytes();assert data==(source/'skills'/name/'SKILL.md').read_bytes();result.append(dict(path=str(path),sha256=hashlib.sha256(data).hexdigest()))
  assert (target/'.ai-redteam/tools').is_dir()
  return result
 checks=[]
 with tempfile.TemporaryDirectory() as directory:
  root=Path(directory)
  for host in HOSTS:
   target=root/host;target.mkdir();assert install(target,host).returncode==0
   files=verify(target,host);before=tree(target);assert install(target,host).returncode!=0 and tree(target)==before
   checks.append(dict(host=host,empty_directory_copy='pass',existing_install_refused=True,files=files,runtime_agent_load='not tested',model_calls=0))
  target=root/'combined';target.mkdir();(target/'AGENTS.md').write_text('Existing project instructions.\n')
  for host in HOSTS:assert install(target,host).returncode==0;verify(target,host)
  assert (target/'AGENTS.md').read_text()=='Existing project instructions.\n'
  corrupt=root/'changed-support';corrupt.mkdir();assert install(corrupt,'cursor').returncode==0
  (corrupt/'.ai-redteam/tools').chmod(0o755)
  (corrupt/'.ai-redteam/tools/unreviewed.txt').write_text('modified support');before=tree(corrupt)
  assert install(corrupt,'codex').returncode!=0 and tree(corrupt)==before and not (corrupt/'.agents').exists()
 commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
 return dict(source_commit=commit,checked_on='2026-10-16',checks=checks,multi_host_same_project=list(HOSTS),existing_project_instructions_preserved=True,modified_support_refused_before_new_host_write=True,model_calls=0)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path);p.add_argument('--receipt',type=Path);a=p.parse_args();result=check(a.source)
 if a.receipt:a.receipt.write_text(json.dumps(result,indent=2)+'\n')
 print('Three empty installs, multi-host reuse, repeat refusal, changed-support refusal and AGENTS preservation pass')
if __name__=='__main__':main()
