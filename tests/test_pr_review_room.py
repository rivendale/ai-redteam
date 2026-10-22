#!/usr/bin/env python3
"""Offline output budget and safe stop-reason controls."""
import contextlib,importlib.util,io,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_pr_review_action import m,event,env,Transport
class Reply(Transport):
 def __init__(self,reason='end_turn',text='Complete synthetic review.'):
  super().__init__();self.reason=reason;self.text=text;self.providers=0
 def __call__(self,url,headers,data=None):
  if url.endswith('/messages'):
   self.providers+=1;packet=json.loads(data)
   assert packet['max_tokens']==16384
   return json.dumps({'stop_reason':self.reason,'content':[{'type':'text','text':self.text}]}).encode()
  return super().__call__(url,headers,data)
class Room(unittest.TestCase):
 def test_budget_and_complete_text(self):
  t=Reply();r=m.review(event(),env(),t);self.assertEqual(r['text'],'Complete synthetic review.');self.assertEqual(t.providers,1)
 def test_stop_reason_codes_never_publish_or_retry(self):
  for reason in ('max_tokens','stop_sequence','tool_use','pause_turn','refusal','model_context_window_exceeded',None,'synthetic-secret-echo'):
   t=Reply(reason)
   with self.assertRaises(m.Refuse) as error:m.review(event(),env(),t)
   self.assertEqual(t.providers,1)
   output=io.StringIO()
   with patch.object(m.os,'environ',{'GITHUB_EVENT_PATH':'fixture'}),patch.object(m.Path,'read_bytes',side_effect=error.exception),contextlib.redirect_stderr(output):self.assertEqual(m.main(),1)
   expected=reason if reason in ('max_tokens','stop_sequence','tool_use','pause_turn','refusal','model_context_window_exceeded') else 'unknown'
   self.assertIn('model_incomplete:'+expected,output.getvalue());self.assertNotIn('synthetic-secret-echo',output.getvalue())
 def test_character_ceiling_retained(self):
  with self.assertRaises(m.Refuse) as error:m.review(event(),env(),Reply(text='x'*32001))
  self.assertEqual(error.exception.code,'model_output_limit')
if __name__=='__main__':unittest.main()
