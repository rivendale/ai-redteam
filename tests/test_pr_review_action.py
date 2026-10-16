#!/usr/bin/env python3
"""Offline trust-boundary tests. Never reads the real process environment or network."""
import ast,copy,hashlib,importlib.util,json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('review_action',ROOT/'tools/pr_review_action.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
HEAD='a'*40;BASE='b'*40;MERGE='c'*40
class Tripwire(dict):
 def __getitem__(self,key):
  if key in ('ANTHROPIC_API_KEY','GITHUB_TOKEN'):raise AssertionError('secret accessed before eligibility')
  return super().__getitem__(key)
 def get(self,key,default=None):
  if key in ('ANTHROPIC_API_KEY','GITHUB_TOKEN'):raise AssertionError('secret accessed before eligibility')
  return super().get(key,default)
def event(fork=False):return {'repository':{'full_name':'example/review'},'number':7,'pull_request':{'number':7,'title':'fixture','body':'review this data','changed_files':1,'head':{'sha':HEAD,'repo':{'full_name':'elsewhere/fork' if fork else 'example/review','fork':fork}},'base':{'sha':BASE,'repo':{'full_name':'example/review'}}}}
def env():return {'GITHUB_EVENT_NAME':'pull_request_target','GITHUB_REPOSITORY':'example/review','AI_REDTEAM_ENABLED':'true','AI_REDTEAM_MODEL':'fixture-model','ANTHROPIC_API_KEY':'synthetic-model-value','GITHUB_TOKEN':'synthetic-read-value'}
class Transport:
 def __init__(self,payload=None,move=False):self.calls=[];self.pr=(payload or event())['pull_request'];self.move=move;self.gets=0
 def __call__(self,url,headers,data=None):
  self.calls.append((url,headers,data))
  if url.endswith('/messages'):
   packet=json.loads(data);assert packet['max_tokens']<=4096 and 'tools' not in packet
   assert 'synthetic-model-value' not in json.dumps(packet)
   return json.dumps({'stop_reason':'end_turn','content':[{'type':'text','text':'<img src="https://invalid.example/">\nREVIEWED: fixture; incomplete context.'}]}).encode()
  if '/compare/' in url:return json.dumps({'merge_base_commit':{'sha':MERGE}}).encode()
  if headers.get('Accept')=='application/vnd.github.diff':return b'diff --git a/a.py b/a.py\n+print("fixture")\n'
  self.gets+=1;p=copy.deepcopy(self.pr)
  if self.move and self.gets>1:p['head']['sha']='d'*40
  return json.dumps(p).encode()
class ActionTests(unittest.TestCase):
 def test_fork_cannot_reach_either_secret_or_transport(self):
  transport=Transport();self.assertIsNone(m.review(event(True),Tripwire(env()),transport));self.assertEqual(transport.calls,[])
 def test_fork_flag_refuses_even_with_forged_same_repo_name(self):
  p=event(True);p['pull_request']['head']['repo']['full_name']='example/review';self.assertIsNone(m.review(p,Tripwire(env()),Transport()))
 def test_opt_out_cannot_reach_secret(self):
  e=env();e['AI_REDTEAM_ENABLED']='false';self.assertIsNone(m.review(event(),Tripwire(e),Transport()))
 def test_ordinary_pull_request_event_cannot_reach_secret(self):
  e=env();e['GITHUB_EVENT_NAME']='pull_request';self.assertIsNone(m.review(event(),Tripwire(e),Transport()))
 def test_foreign_nonfork_repo_cannot_reach_secrets(self):
  p=event();p['pull_request']['head']['repo']['full_name']='elsewhere/review';t=Transport();self.assertIsNone(m.review(p,Tripwire(env()),t));self.assertEqual(t.calls,[])
 def test_dependabot_actor_skips_before_secret_read(self):
  e=env();e['GITHUB_ACTOR']='dependabot[bot]';self.assertIsNone(m.review(event(),Tripwire(e),Transport()))
 def test_dependabot_author_skips_even_when_event_actor_is_human(self):
  p=event();p['pull_request']['user']={'login':'dependabot[bot]'};self.assertIsNone(m.review(p,Tripwire(env()),Transport()))
 def test_exact_allowlisted_secret_bearing_steps(self):
  # Every added command/step changes the secret boundary and needs review.
  s=(ROOT/'.github/workflows/pr-review.yml').read_text()
  self.assertEqual(re.findall(r'^jobs:',s,re.M),['jobs:'])
  self.assertEqual(re.findall(r'^  ([^ :]+):',s.split('jobs:\n',1)[1],re.M),['review'])
  self.assertEqual(hashlib.sha256(s.encode()).hexdigest(),'31120e04be5f5a80cb63c6817e1d2a8a8f8b3776721d4ff385f89fba00058dab','any workflow change needs a fresh review of this allowlist')
  expected="""      - name: Check out trusted base only
        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
        with:
          ref: ${{ github.event.pull_request.base.sha }}
          persist-credentials: false
      - name: Generate one bounded review round
        env:
          AI_REDTEAM_ENABLED: ${{ vars.AI_REDTEAM_ENABLED }}
          AI_REDTEAM_MODEL: ${{ vars.AI_REDTEAM_MODEL }}
          ANTHROPIC_API_KEY: ${{ secrets.AI_REDTEAM_MODEL_KEY }}
          GITHUB_TOKEN: ${{ github.token }}
        run: python3 tools/pr_review_action.py
"""
  self.assertEqual(s.count('    steps:\n'),1);self.assertEqual(s.split('    steps:\n',1)[1],expected)
  self.assertEqual(len(re.findall(r'^\s*(?:- )?run:',s,re.M)),1)
 def test_one_bounded_tool_free_model_request_with_frozen_head(self):
  t=Transport();r=m.review(event(),env(),t);self.assertEqual(r['head'],HEAD);self.assertEqual(r['merge_base'],MERGE);self.assertEqual(sum(url.endswith('/messages') for url,_,_ in t.calls),1)
  self.assertTrue(all(data is None for url,_,data in t.calls if not url.endswith('/messages')))
  text=m.render(r);self.assertNotIn('<img',text);self.assertIn('&lt;img',text)
 def test_moved_head_refuses_publication(self):
  with self.assertRaises(m.Refuse):m.review(event(),env(),Transport(move=True))
 def test_payload_is_data_not_a_shell_or_file_write(self):
  p=event();p['pull_request']['title']='$(touch should-not-exist)';t=Transport(p);m.review(p,env(),t);self.assertFalse((ROOT/'should-not-exist').exists())
 def test_live_metadata_cannot_upgrade_a_fork_to_trusted(self):
  with self.assertRaises(m.Refuse):m.review(event(),env(),Transport(event(True)))
 def test_workflow_gate_is_false_for_fork_before_secret_job(self):
  s=(ROOT/'.github/workflows/pr-review.yml').read_text();expr=re.search(r'^    if: \$\{\{ (.+) \}\}$',s,re.M)[1]
  def evaluate(fork,name='example/review',actor='human',author='human'):
   text=expr
   for key,value in {'vars.AI_REDTEAM_ENABLED':'true','github.event.pull_request.head.repo.fork':fork,'github.event.pull_request.head.repo.full_name':name,'github.repository':'example/review','github.actor':actor,'github.event.pull_request.user.login':author}.items():text=text.replace(key,repr(value))
   text=text.replace('always()','True').replace('||','or').replace('&&','and').replace('== false','== False');node=ast.parse(text,mode='eval');self.assertTrue(all(isinstance(n,(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.Compare,ast.Eq,ast.NotEq,ast.Constant)) for n in ast.walk(node)));return eval(compile(node,'workflow-gate','eval'),{'__builtins__':{}},{})
  self.assertFalse(evaluate(True));self.assertFalse(evaluate(True,'elsewhere/fork'));self.assertTrue(evaluate(False));self.assertFalse(evaluate(False,'elsewhere/fork'));self.assertFalse(evaluate(False,actor='dependabot[bot]'));self.assertFalse(evaluate(False,author='dependabot[bot]'))
  self.assertIn('contents: read',s);self.assertIn('pull-requests: read',s);self.assertNotIn(': write',s)
  self.assertIn('ref: ${{ github.event.pull_request.base.sha }}',s);self.assertIn('persist-credentials: false',s)
  self.assertNotIn('run: ${{',s);self.assertNotIn('pull_request.head.sha }}',s)
if __name__=='__main__':unittest.main()
