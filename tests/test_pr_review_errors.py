#!/usr/bin/env python3
"""Offline diagnostics checks; only synthetic credentials and responses."""
import contextlib, http.client, importlib.util, io, json, socket, sys, unittest, urllib.error
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('action',ROOT/'tools/pr_review_action.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
KEY='synthetic-secret-never-log';TOKEN='synthetic-token-never-log'
PROVIDER='https://api.anthropic.com/v1/messages'
class Opener:
 def __init__(self,error):self.error=error;self.calls=0
 def open(self,*args,**kwargs):self.calls+=1;raise self.error
class Diagnostics(unittest.TestCase):
 def run_failure(self,error,url=PROVIDER):
  opener=Opener(error)
  with patch.object(m.urllib.request,'build_opener',return_value=opener):
   with self.assertRaises(m.Refuse) as caught:m.exchange(url,{'x-api-key':KEY})
  output=io.StringIO()
  with patch.object(m,'review',side_effect=caught.exception),patch.object(m.os,'environ',{'GITHUB_EVENT_PATH':'fixture'}),patch.object(m.Path,'read_bytes',return_value=b'{}'),contextlib.redirect_stderr(output):
   self.assertEqual(m.main(),1)
  self.assertEqual(opener.calls,1)
  text=output.getvalue()
  for forbidden in (KEY,TOKEN,'response details','hostile.example','x-api-key','Authorization'):self.assertNotIn(forbidden,text)
  return text
 def http(self,status,error_type,body=None):
  raw=json.dumps(body or {'error':{'type':error_type,'message':KEY+' response details '+TOKEN}}).encode()
  return urllib.error.HTTPError(PROVIDER,status,KEY,{'Authorization':TOKEN},io.BytesIO(raw))
 def test_provider_statuses(self):
  for status,kind in ((401,'authentication_error'),(404,'not_found_error'),(400,'invalid_request_error')):
   with self.subTest(status=status):self.assertIn(f'provider HTTP {status} {kind}',self.run_failure(self.http(status,kind)))
 def test_timeout(self):self.assertIn('provider timeout',self.run_failure(socket.timeout(KEY)))
 def test_wrapped_timeout(self):self.assertIn('provider timeout',self.run_failure(urllib.error.URLError(socket.timeout(KEY))))
 def test_network(self):self.assertIn('provider network',self.run_failure(urllib.error.URLError(KEY)))
 def test_github_is_not_provider(self):
  text=self.run_failure(self.http(404,'not_found_error'),'https://api.github.com/repos/example/test')
  self.assertIn('github HTTP 404',text);self.assertNotIn('provider',text)
 def test_type_echoing_key_is_suppressed(self):self.assertIn('unknown_error',self.run_failure(self.http(401,KEY)))
 def test_arbitrary_type_and_newline_are_suppressed(self):
  self.assertIn('unknown_error',self.run_failure(self.http(400,'hostile.example\n'+TOKEN)))
 def test_malformed_and_oversized_error(self):
  for raw in (b'not json '+KEY.encode(),b'x'*(m.LIMIT+1),b'[]',b'{"error": []}'):
   with self.subTest(size=len(raw)):
    error=urllib.error.HTTPError(PROVIDER,400,KEY,{},io.BytesIO(raw))
    self.assertIn('provider HTTP 400 unknown_error',self.run_failure(error))
 def test_local_error_does_not_log_exception(self):
  output=io.StringIO()
  with patch.object(m.os,'environ',{'GITHUB_EVENT_PATH':'fixture'}),patch.object(m.Path,'read_bytes',side_effect=OSError(KEY)),contextlib.redirect_stderr(output):
   self.assertEqual(m.main(),1)
  self.assertIn('configuration/input/response',output.getvalue());self.assertNotIn(KEY,output.getvalue())
class Followup(unittest.TestCase):
 run_failure=Diagnostics.run_failure
 http=Diagnostics.http
 def test_http_parser_failures_are_network(self):
  for error in (http.client.BadStatusLine(KEY),http.client.IncompleteRead(KEY.encode(),100)):
   with self.subTest(kind=type(error).__name__):self.assertIn('provider network',self.run_failure(error))
 def test_unexpected_cli_failures_never_trace_back(self):
  for error in (RecursionError(KEY),RuntimeError(KEY),MemoryError(KEY)):
   output=io.StringIO()
   with patch.object(m.os,'environ',{'GITHUB_EVENT_PATH':'fixture'}),patch.object(m.Path,'read_bytes',side_effect=error),contextlib.redirect_stderr(output):self.assertEqual(m.main(),1)
   self.assertIn('unexpected_error',output.getvalue());self.assertNotIn(KEY,output.getvalue());self.assertNotIn('Traceback',output.getvalue())
 def test_local_refusal_codes(self):
  pairs={'diff absent or too large; no silent truncation':'diff_limit','changed-file limit exceeded or unavailable':'file_limit','PR identity moved or became ineligible; no current-head report':'identity_moved','redirect refused':'redirect','model did not finish a text review; no automatic retry':'model_incomplete','credential reflection refused; output discarded':'credential_reflection','model secret missing':'model_secret_missing','provider response invalid':'provider_response_invalid'}
  for reason,code in pairs.items():
   output=io.StringIO()
   with patch.object(m.os,'environ',{'GITHUB_EVENT_PATH':'fixture'}),patch.object(m.Path,'read_bytes',side_effect=m.Refuse(reason)),contextlib.redirect_stderr(output):self.assertEqual(m.main(),1)
   self.assertIn('local '+code,output.getvalue())
 def test_unknown_local_text_is_suppressed(self):
  output=io.StringIO()
  with patch.object(m.os,'environ',{'GITHUB_EVENT_PATH':'fixture'}),patch.object(m.Path,'read_bytes',side_effect=m.Refuse(KEY)),contextlib.redirect_stderr(output):self.assertEqual(m.main(),1)
  self.assertIn('local local_refusal',output.getvalue());self.assertNotIn(KEY,output.getvalue())
 def test_invalid_http_status_is_suppressed(self):
  self.assertIn('provider HTTP unknown',self.run_failure(self.http(999,'authentication_error')))
if __name__=='__main__':unittest.main()
