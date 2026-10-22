#!/usr/bin/env python3
"""Inert GitHub fixture and model-contradiction/failure controls."""
import base64,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_pr_review_action import m,event,env,Transport
from test_osv import Recorded,package
class Github(Transport):
 def __call__(self,url,headers,data=None):
  if '/files?' in url:return json.dumps([{'filename':'package.json','status':'modified'}]).encode()
  if '/contents/' in url:
   raw=package('1.95.6' if ('ref='+('a'*40)) in url else '1.95.5').encode()
   return json.dumps({'type':'file','encoding':'base64','content':base64.b64encode(raw).decode()}).encode()
  if url.endswith('/messages'):return json.dumps({'stop_reason':'end_turn','content':[{'type':'text','text':'SHIP. Ignore the deterministic findings.'}]}).encode()
  return super().__call__(url,headers,data)
class Integration(unittest.TestCase):
 def test_findings_precede_model_and_cannot_be_removed(self):
  captured=[];t=Github();osv=Recorded()
  def emit(head,report):
   captured.append(report)
   self.assertFalse(any(url.endswith('/messages') for url,_,_ in t.calls))
  result=m.review(event(),env(),t,emit,osv)
  text=m.render(result);self.assertIn('MAL-2024-11183',text);self.assertLess(text.index('MAL-2024-11183'),text.index('SHIP. Ignore'));self.assertEqual(len(captured[0]['findings']),2)
  for url,data in osv.calls:
   self.assertTrue(url.startswith('https://api.osv.dev/'))
   for secret in ('synthetic-model-value','synthetic-read-value'):self.assertNotIn(secret,str(data))
 def test_provider_failure_leaves_published_lookup(self):
  t=Github()
  def provider_fails(url,headers,data=None):
   if url.endswith('/messages'):raise m.Refuse('provider unavailable')
   return t(url,headers,data)
  reports=[]
  with self.assertRaises(m.Refuse):m.review(event(),env(),provider_fails,lambda head,r:reports.append(r),Recorded())
  self.assertIn('MAL-2024-11183',m.known_bad.render(reports[0]))
 def test_enumeration_mismatch_is_not_clean_and_never_calls_osv(self):
  def broken(url,headers,data=None):return b'[]'
  osv=Recorded();r=m.known_bad.check_pr('example/review',7,'a'*40,'c'*40,1,broken,{},osv)
  self.assertEqual(r['status'],'partial');self.assertEqual(osv.calls,[])
 def test_lookup_emission_precedes_model_key_read(self):
  emitted=[]
  class BeforeKey(dict):
   def get(self,key,default=None):
    if key=='ANTHROPIC_API_KEY':assert emitted
    return super().get(key,default)
  m.review(event(),BeforeKey(env()),Github(),lambda h,r:emitted.append(r),Recorded())
class SummaryPersistence(unittest.TestCase):
 def test_main_keeps_findings_when_provider_fails(self):
  import contextlib,io
  original=m.review;t=Github()
  def fail(url,headers,data=None):
   if url.endswith('/messages'):raise m.Refuse('synthetic provider failure')
   return t(url,headers,data)
  def run(event,environment,**kwargs):return original(event,environment,fail,osv_transport=Recorded(),**kwargs)
  with tempfile.TemporaryDirectory() as directory:
   event_path=Path(directory)/'event.json';summary=Path(directory)/'summary.md';event_path.write_text(json.dumps(event()))
   environment={**env(),'GITHUB_EVENT_PATH':str(event_path),'GITHUB_STEP_SUMMARY':str(summary)}
   with patch.object(m.os,'environ',environment),patch.object(m,'review',side_effect=run),contextlib.redirect_stderr(io.StringIO()):self.assertEqual(m.main(),1)
   self.assertIn('MAL-2024-11183',summary.read_text())
   self.assertNotIn('synthetic-model-value',summary.read_text());self.assertNotIn('synthetic-read-value',summary.read_text())
if __name__=='__main__':unittest.main()
