#!/usr/bin/env python3
"""Offline dependency lookup controls. Recorded API responses, never package execution."""
import importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import known_bad as m
FIX=ROOT/'tests/osv'
class Recorded:
 def __init__(self):self.calls=[]
 def __call__(self,url,data=None):
  self.calls.append((url,data))
  if url.endswith('/querybatch'):
   queries=json.loads(data)['queries'];result=[]
   for q in queries:
    if q.get('package',{}).get('name')=='@solana/web3.js' and q.get('version')=='1.95.6':result.append(json.loads((FIX/'batch.json').read_text())['results'][0])
    else:result.append({})
   return json.dumps({'results':result}).encode()
  return (FIX/(url.rsplit('/',1)[-1]+'.json')).read_bytes()
def change(path,before,after):return {'path':path,'before':before,'after':after}
def package(version):return json.dumps({'dependencies':{'@solana/web3.js':version}})
class LookupTests(unittest.TestCase):
 def test_recorded_malicious_and_clean_bump(self):
  t=Recorded();r=m.scan_changes([change('package.json',package('1.95.5'),package('1.95.6'))],t)
  self.assertEqual(r['status'],'complete');self.assertEqual(len(r['findings']),2)
  self.assertTrue(any('MAL-2024-11183' in f['id'] for f in r['findings']))
  for f in r['findings']:
   self.assertIn(f['severity'],('P1','P2'));self.assertIn('package.json:',f['location']);self.assertTrue(f['advisory'].startswith('https://osv.dev/vulnerability/'));self.assertTrue(f['osv_severity']);self.assertTrue(f['scenario']);self.assertTrue(f['suggested_test'])
  clean=m.scan_changes([change('package.json',package('1.95.6'),package('1.95.8'))],Recorded());self.assertEqual(clean['findings'],[]);self.assertEqual(clean['status'],'complete')
 def test_unchanged_and_removal_make_no_requests(self):
  for after in (package('1.95.6'),'{}'):
   t=Recorded();r=m.scan_changes([change('package.json',package('1.95.6'),after)],t);self.assertEqual(t.calls,[]);self.assertEqual(r['findings'],[])
 def test_each_ecosystem_extracts_added_version(self):
  samples=[('package-lock.json','{"lockfileVersion":3,"packages":{"node_modules/a":{"version":"1.2.3","resolved":"https://registry.npmjs.org/a/-/a-1.2.3.tgz"}}}','npm','a','1.2.3'),('requirements.txt','Example_Pkg==1.2.3\n','PyPI','example-pkg','1.2.3'),('go.mod','module example.org/app\nrequire (\n example.org/a v1.2.3\n)\n','Go','example.org/a','v1.2.3'),('Cargo.lock','[[package]]\nname="fixture"\nversion="1.2.3"\nsource="registry+https://github.com/rust-lang/crates.io-index"\n','crates.io','fixture','1.2.3'),('.github/workflows/a.yml','jobs:\n  x:\n    steps:\n      - uses: example/action@v1.2.3\n','GitHub Actions','example/action','1.2.3')]
  for path,text,eco,name,version in samples:
   with self.subTest(path=path):
    records,gaps=m.parse(path,text);self.assertEqual(gaps,[]);self.assertTrue(any(x['ecosystem']==eco and x['name']==name and x['version']==version for x in records))
 def test_sha_action_uses_commit_query(self):
  r=m.scan_changes([change('.github/workflows/a.yml','',f'- uses: example/action@'+('a'*40)+'\n')],Recorded());self.assertEqual(r['queries'],[{'commit':'a'*40}])
 def test_unsupported_is_never_clean(self):
  for path,text in [('package.json','{"dependencies":{"a":"^1.2.3"}}'),('package.json','no json'),('yarn.lock','a@^1:'),('pnpm-lock.yaml','lockfileVersion: 9'),('requirements.txt','a>=1.2'),('Cargo.toml','[dependencies]\na="1.2"'),('go.mod','replace example/a => ../a'),('.github/workflows/a.yml','- uses: example/action@v4\n')]:
   with self.subTest(path=path):
    r=m.scan_changes([change(path,'',text)],Recorded());self.assertNotEqual(r['status'],'complete');self.assertIn('known-bad check did not run',m.render(r))
 def test_unreachable_is_explicit(self):
  def offline(*args):raise TimeoutError('private remote text')
  r=m.scan_changes([change('package.json','{}',package('1.95.6'))],offline);self.assertEqual(r['status'],'partial');self.assertIn('known-bad check did not run',m.render(r));self.assertNotIn('private remote text',m.render(r))
 def test_bad_batch_shape_and_pagination_never_clean(self):
  for reply in ({},{'results':[]},{'results':[{'next_page_token':'more'}]},{'results':[{'error':{'message':'bad'}}]}):
   r=m.scan_changes([change('package.json','{}',package('1.95.6'))],lambda *a:json.dumps(reply).encode());self.assertEqual(r['status'],'partial')
 def test_detail_failure_retains_matching_id(self):
  t=Recorded()
  def missing(url,data=None):
   if '/vulns/' in url:raise TimeoutError()
   return t(url,data)
  r=m.scan_changes([change('package.json','{}',package('1.95.6'))],missing);self.assertEqual(len(r['findings']),2);self.assertEqual(r['status'],'partial');self.assertIn('MAL-2024-11183',m.render(r))
 def test_query_limit_is_visible(self):
  data=json.dumps({'dependencies':{f'fixture{i}':'1.2.3' for i in range(m.MAX_QUERIES+1)}});t=Recorded();r=m.scan_changes([change('package.json','{}',data)],t);self.assertEqual(r['status'],'partial');self.assertEqual(t.calls,[])
 def test_renamed_manifest_treats_head_as_added(self):
  r=m.scan_changes([change('nested/package.json','',package('1.95.6'))],Recorded());self.assertEqual(len(r['findings']),2)
if __name__=='__main__':unittest.main()
