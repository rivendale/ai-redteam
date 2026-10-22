#!/usr/bin/env python3
"""Bounded OSV lookup over inert base/head manifest text. Standard library only."""
import base64,html,http.client,json,re,time,tomllib,urllib.request
from pathlib import PurePosixPath
from urllib.parse import quote
MAX_QUERIES=100
MAX_FILES=20
MAX_DETAILS=20
MAX_MATCHES=200
LIMIT=2*1024*1024
class Incomplete(ValueError):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise Incomplete('redirect')
class OSV:
 """Fixed public destination, no credentials, 21 calls, a 60-second deadline between reads, 10-second socket timeout."""
 def __init__(self):self.deadline=time.monotonic()+60;self.calls=0
 def __call__(self,url,data=None):
  if not (url=='https://api.osv.dev/v1/querybatch' or re.fullmatch(r'https://api\.osv\.dev/v1/vulns/[A-Za-z0-9._-]{1,160}',url)):raise Incomplete('destination')
  remaining=self.deadline-time.monotonic()
  if self.calls>=1+MAX_DETAILS or remaining<=0:raise Incomplete('budget')
  self.calls+=1
  request=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json','Accept':'application/json'})
  with urllib.request.build_opener(NoRedirect).open(request,timeout=min(10,remaining)) as response:
   parts=[];size=0
   while True:
    if time.monotonic()>self.deadline:raise Incomplete('deadline')
    chunk=response.read(min(65536,LIMIT+1-size))
    if not chunk:break
    parts.append(chunk);size+=len(chunk)
    if size>LIMIT:raise Incomplete('size')
  return b''.join(parts)
def requirements(path):
 p=PurePosixPath(path)
 return bool(re.fullmatch(r'(?:requirements|constraints)[^/]*\.(?:txt|in)',p.name)) or (bool(set(p.parts[:-1])&{'requirements','constraints'}) and p.suffix in ('.txt','.in'))
def relevant(path):
 name=PurePosixPath(path).name
 return (name in ('package.json','package-lock.json','npm-shrinkwrap.json','yarn.lock','pnpm-lock.yaml','bun.lock','bun.lockb','pyproject.toml','poetry.lock','uv.lock','Pipfile','Pipfile.lock','setup.py','setup.cfg','go.mod','go.sum','Cargo.toml','Cargo.lock')
         or requirements(path)
         or (path.startswith('.github/workflows/') and name.endswith(('.yml','.yaml'))))
def parse(path,text):
 """Return exact resolved references plus explicit gaps; no resolver, imports or package execution."""
 records=[];gaps=[];name=PurePosixPath(path).name
 def gap():
  if path not in gaps:gaps.append(path)
 def add(eco,pkg,version,needle=None,commit=False):
  if eco=='PyPI':pkg=re.sub(r'[-_.]+','-',pkg).lower()
  valid_name=(r'(@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+' if eco=='npm' else r'[A-Za-z0-9][A-Za-z0-9._/+-]*')
  if not isinstance(pkg,str) or not re.fullmatch(valid_name,pkg) or len(pkg)>240:gap();return
  if not isinstance(version,str) or len(version)>160:gap();return
  if commit:
   if not re.fullmatch(r'[0-9a-fA-F]{40}',version):gap();return
  elif not re.fullmatch(r'v?\d+(?:\.\d+)+(?:[-+._A-Za-z0-9]*)',version):gap();return
  elif eco=='npm' and not re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][A-Za-z0-9_.-]+)?',version):gap();return
  offset=text.find(needle or pkg);line=text.count('\n',0,max(0,offset))+1
  records.append({'ecosystem':eco,'name':pkg,'version':version,'commit':commit,'location':path+':'+str(line)})
 if not text.strip():return records,gaps
 try:
  if name=='package.json':
   obj=json.loads(text)
   if obj.get('overrides') or obj.get('resolutions'):gap()
   for section in ('dependencies','devDependencies','optionalDependencies','peerDependencies'):
    for pkg,version in obj.get(section,{}).items():add('npm',pkg,version)
  elif name in ('package-lock.json','npm-shrinkwrap.json'):
   obj=json.loads(text)
   if obj.get('lockfileVersion') in (2,3) and isinstance(obj.get('packages'),dict):
    for pathkey,p in obj['packages'].items():
     if not pathkey:continue
     if 'node_modules/' not in pathkey or p.get('link'):gap();continue
     pkg=p.get('name') or pathkey.rsplit('node_modules/',1)[-1]
     if p.get('resolved') and not p['resolved'].startswith('https://registry.npmjs.org/'):gap();continue
     add('npm',pkg,p.get('version'),pathkey)
   elif obj.get('lockfileVersion')==1:
    def walk(deps):
     for pkg,p in deps.items():
      if p.get('resolved') and not p['resolved'].startswith('https://registry.npmjs.org/'):gap();continue
      add('npm',pkg,p.get('version'));walk(p.get('dependencies',{}))
    walk(obj.get('dependencies',{}))
   else:gap()
  elif name in ('poetry.lock','uv.lock'):
   obj=tomllib.loads(text)
   for p in obj.get('package',[]):
    source=p.get('source',{})
    if source and not (source.get('type')=='legacy' or source.get('registry') in ('https://pypi.org/simple','https://pypi.org/simple/')):gap();continue
    add('PyPI',p['name'],p.get('version'))
  elif name=='Pipfile.lock':
   obj=json.loads(text)
   for section in ('default','develop'):
    for pkg,p in obj.get(section,{}).items():
     version=p.get('version','')
     if not version.startswith('==') or any(k in p for k in ('git','path','file')):gap();continue
     add('PyPI',pkg,version[2:])
  elif name=='pyproject.toml':
   obj=tomllib.loads(text);project=obj.get('project',{})
   if project.get('dynamic'):gap()
   specs=list(project.get('dependencies',[]))+list(obj.get('build-system',{}).get('requires',[]))
   for group in project.get('optional-dependencies',{}).values():specs.extend(group)
   for group in obj.get('dependency-groups',{}).values():specs.extend(group)
   for spec in specs:
    if not isinstance(spec,str):gap();continue
    match=re.fullmatch(r'\s*([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?\s*==\s*([^;\s]+)(?:\s*;.*)?',spec)
    if not match:gap();continue
    add('PyPI',match[1],match[2])
   poetry=obj.get('tool',{}).get('poetry',{})
   poetry_deps=dict(poetry.get('dependencies',{}))
   if poetry.get('dev-dependencies') or poetry.get('group'):gap()
   for pkg,v in poetry_deps.items():
    if pkg=='python':continue
    if isinstance(v,dict) and any(k in v for k in ('git','path','url','source')):gap();continue
    add('PyPI',pkg,v if isinstance(v,str) else v.get('version'))
  elif requirements(path):
   for line in text.splitlines():
    line=line.split(' #',1)[0].strip()
    if not line or line.startswith('#'):continue
    match=re.fullmatch(r'([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?==([^;\s]+)(?:\s*;.*)?',line)
    if not match:gap();continue
    add('PyPI',match[1],match[2])
  elif name=='go.mod':
   block=False
   for line in text.splitlines():
    line=line.split('//',1)[0].strip()
    if line=='require (':block=True;continue
    if line==')':block=False;continue
    if line.startswith('replace'):gap()
    match=re.fullmatch(r'(?:require\s+)?([^\s]+)\s+(v\S+)',line)
    if match and (block or line.startswith('require ')):add('Go',match[1],match[2])
    elif (block and line) or line.startswith('require'):gap()
  elif name=='go.sum':
   for line in text.splitlines():
    if not line.strip():continue
    parts=line.split()
    if len(parts)!=3:gap();continue
    add('Go',parts[0],parts[1].removesuffix('/go.mod'))
  elif name=='Cargo.lock':
   for p in tomllib.loads(text).get('package',[]):
    source=p.get('source')
    if source is None:continue # workspace package, not a registry dependency
    if source not in ('registry+https://github.com/rust-lang/crates.io-index','sparse+https://index.crates.io/'):gap();continue
    add('crates.io',p['name'],p['version'])
  elif name=='Cargo.toml':
   obj=tomllib.loads(text)
   tables=[obj]+list(obj.get('target',{}).values())
   for table in tables:
    for section in ('dependencies','dev-dependencies','build-dependencies'):
     for pkg,p in table.get(section,{}).items():
      version=p if isinstance(p,str) else p.get('version','')
      if not isinstance(version,str) or not version.startswith('=') or (isinstance(p,dict) and any(k in p for k in ('git','path','workspace','registry'))):gap();continue
      add('crates.io',p.get('package',pkg) if isinstance(p,dict) else pkg,version[1:])
   if 'workspace' in obj and obj['workspace'].get('dependencies'):gap()
  elif path.startswith('.github/workflows/'):
   for line in text.splitlines():
    if not re.search(r'\buses\s*[\'\"]?\s*:',line):continue
    match=re.fullmatch(r'\s*(?:-\s*)?[\'\"]?uses[\'\"]?\s*:\s*[\'\"]?([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)@([A-Za-z0-9_.+-]+)[\'\"]?\s*(?:#.*)?',line)
    if not match:gap();continue
    pkg='/'.join(match[1].split('/')[:2]);v=match[2]
    if re.fullmatch(r'[0-9a-fA-F]{40}',v):add('GitHub Actions',pkg,v,match[1],True)
    elif re.fullmatch(r'v?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9_.-]+)?',v):add('GitHub Actions',pkg,v.removeprefix('v'),match[1])
    else:gap()
   if re.search(r'\\|[{}]|\?\s*uses',text):gap() # unsupported YAML forms never imply coverage
  elif relevant(path):gap()
 except (ValueError,TypeError,KeyError,AttributeError,RecursionError):gap()
 return records,gaps
def identity(p):return (p['ecosystem'],p['name'],p['version'],p['commit'])
def query(p):return {'commit':p['version']} if p['commit'] else {'package':{'ecosystem':p['ecosystem'],'name':p['name']},'version':p['version']}
def json_response(raw):
 if not isinstance(raw,bytes) or len(raw)>LIMIT:raise Incomplete('response')
 return json.loads(raw)
def severity(detail):
 # Preserve recognized database levels and raw CVSS vectors; never invent a score.
 values=[]
 def level(value):
  if isinstance(value,str) and value.upper() in ('LOW','MODERATE','MEDIUM','HIGH','CRITICAL'):values.append(value.upper())
 if isinstance(detail.get('database_specific'),dict):level(detail['database_specific'].get('severity'))
 affected=detail.get('affected',[])
 if isinstance(affected,list):
  for record in affected:
   if isinstance(record,dict) and isinstance(record.get('ecosystem_specific'),dict):level(record['ecosystem_specific'].get('severity'))
 vectors=detail.get('severity',[])
 if isinstance(vectors,list):
  for value in vectors:
   if not isinstance(value,dict):continue
   kind=value.get('type');score=value.get('score')
   if kind in ('CVSS_V2','CVSS_V3','CVSS_V4') and isinstance(score,str) and re.fullmatch(r'[A-Za-z0-9:/._-]{1,500}',score):values.append(kind+': '+score)
 return '; '.join(dict.fromkeys(values))[:1000] or 'not supplied by OSV'
def scan_changes(changes,transport=None):
 report={'status':'complete','findings':[],'gaps':[],'queries':[],'files':[]}
 records={};transport=transport or OSV()
 for change in changes:
  path=change['path']
  if not relevant(path):continue
  report['files'].append(path)
  if len(report['files'])>MAX_FILES:report['gaps'].append('dependency file limit');break
  old,oldgaps=parse(path,change.get('before',''));new,gaps=parse(path,change.get('after',''))
  report['gaps'].extend(oldgaps+gaps)
  previous={identity(p) for p in old}
  for p in new:
   if identity(p) not in previous:records.setdefault(identity(p),p)
 if len(records)>MAX_QUERIES:report['gaps'].append('query count limit');records={}
 packages=list(records.values());report['queries']=[query(p) for p in packages]
 if packages:
  try:
   batch=json_response(transport('https://api.osv.dev/v1/querybatch',json.dumps({'queries':report['queries']}).encode()))
   results=batch.get('results') if isinstance(batch,dict) else None
   if not isinstance(results,list) or len(results)!=len(packages):raise Incomplete('alignment')
   details={}
   for package,result in zip(packages,results):
    if not isinstance(result,dict) or any(k not in ('vulns','next_page_token') for k in result):report['gaps'].append('OSV result shape');continue
    if result.get('next_page_token'):report['gaps'].append('OSV pagination unfinished')
    vulns=result.get('vulns',[])
    if not isinstance(vulns,list):report['gaps'].append('OSV result shape');continue
    if len(vulns)>1000:report['gaps'].append('OSV finding limit');vulns=vulns[:1000]
    for v in vulns:
     if len(report['findings'])>=MAX_MATCHES:report['gaps'].append('OSV finding limit');break
     osv_id=v.get('id') if isinstance(v,dict) else None
     if not isinstance(osv_id,str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,160}',osv_id):report['gaps'].append('OSV invalid ID');continue
     if osv_id not in details:
      detail={}
      if len(details)<MAX_DETAILS:
       try:
        detail=json_response(transport('https://api.osv.dev/v1/vulns/'+osv_id))
        if not isinstance(detail,dict) or detail.get('id')!=osv_id:raise Incomplete('detail identity')
       except (ValueError,OSError,TypeError,RecursionError,http.client.HTTPException):report['gaps'].append('OSV detail unavailable');detail={}
      else:report['gaps'].append('OSV detail limit')
      details[osv_id]=detail
     detail=details[osv_id];sev=severity(detail)
     report['findings'].append({'id':osv_id,'severity':'P1' if osv_id.startswith('MAL-') or 'HIGH' in sev.upper() or 'CRITICAL' in sev.upper() else 'P2','osv_severity':sev,'location':package['location'],'scenario':package['ecosystem']+' '+package['name']+'@'+package['version']+' is newly selected and matches OSV '+osv_id+'. Installing or running it may expose the behavior described by that advisory; runtime reachability is not established.','suggested_test':'Replace the selected version with an independently verified unaffected version and rerun the frozen lookup.','advisory':'https://osv.dev/vulnerability/'+osv_id})
  except (ValueError,OSError,TypeError,RecursionError,http.client.HTTPException):report['gaps'].append('OSV request unavailable or invalid')
 if report['gaps']:report['status']='partial'
 elif not report['files']:report['status']='not_applicable'
 return report
def render(report):
 title='Known-bad version lookup: '+report['status']
 if report['status']=='partial':title+='; known-bad check did not run to completion'
 text=title+'\nOSV matches are deterministic inputs, independent of model prose; a zero is not a safety verdict.\n'
 text+='Queried '+str(len(report['queries']))+' added/changed resolved references.\n'
 for gap in sorted(set(report['gaps'])):text+='Coverage gap: '+gap+'\n'
 for f in report['findings']:
  text+='\n'+f['severity']+' '+f['id']+' at '+f['location']+'\nOSV severity: '+f['osv_severity']+'\n'+f['scenario']+'\nSuggested test: '+f['suggested_test']+'\nAdvisory: '+f['advisory']+'\n'
 return '<pre>'+html.escape(text)+'</pre>\n'
def github_changes(repo,number,head,merge,changed_files,transport,headers):
 """Read bounded inert API text only. No Git checkout, credential forwarding or untrusted execution."""
 files=[]
 for page in (1,2):
  values=json_response(transport('https://api.github.com/repos/'+repo+'/pulls/'+str(number)+'/files?per_page=100&page='+str(page),headers))
  if not isinstance(values,list):raise Incomplete('file listing')
  files.extend(values)
  if len(values)<100:break
 if len(files)!=changed_files:raise Incomplete('file listing count')
 selected=[f for f in files if relevant(f.get('filename','')) or relevant(f.get('previous_filename',''))]
 if len(selected)>MAX_FILES:raise Incomplete('dependency file limit')
 def content(path,ref):
  if not isinstance(path,str) or len(path)>1000 or any(p in ('','..','.') for p in path.split('/')):raise Incomplete('path')
  url='https://api.github.com/repos/'+repo+'/contents/'+quote(path,safe='/')+'?ref='+ref
  obj=json_response(transport(url,headers))
  if not isinstance(obj,dict) or obj.get('type')!='file' or obj.get('encoding')!='base64':raise Incomplete('file contents')
  raw=base64.b64decode(obj['content'].replace('\n',''),validate=True)
  if len(raw)>LIMIT:raise Incomplete('file size')
  return raw.decode('utf-8')
 changes=[]
 for f in selected:
  path=f['filename'];status=f.get('status')
  if status not in ('added','removed','modified','renamed'):raise Incomplete('file status')
  before=content(f.get('previous_filename',path),merge) if status!='added' else ''
  after=content(path,head) if status!='removed' else ''
  changes.append({'path':path if relevant(path) else f['previous_filename'],'before':before,'after':after})
 return changes
def gap_report(reason):
 return {'status':'partial','findings':[],'gaps':[reason],'queries':[],'files':[]}
def check_pr(repo,number,head,merge,changed_files,transport,headers,osv_transport=None):
 try:return scan_changes(github_changes(repo,number,head,merge,changed_files,transport,headers),osv_transport)
 except (ValueError,OSError,TypeError,KeyError,RecursionError,http.client.HTTPException):return gap_report('dependency enumeration unavailable or over limit')
