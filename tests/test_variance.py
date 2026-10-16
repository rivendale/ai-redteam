#!/usr/bin/env python3
import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('variance',ROOT/'tools/report_variance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(identity,hit,alarm=0,control=False):return {'id':identity,'control':control,'planted':0 if control else 1,'recall_hits':hit,'false_alarm':alarm,'verdict':'SHIP','parse_error':False,'signature':str(hit)+':'+str(alarm)}
def runs():return [[row('A',1),row('B',0),row('C',0,control=True)],[row('A',1),row('B',1),row('C',0,1,True)],[row('A',1),row('B',0),row('C',0,control=True)]]
class VarianceTests(unittest.TestCase):
 def test_three_run_spreads_and_case_agreement(self):
  r=m.summarize(runs());self.assertEqual(r['recall_pct']['values'],[50,100,50]);self.assertEqual(r['recall_pct']['spread'],50);self.assertEqual(r['false_alarms']['values'],[0,1,0]);self.assertEqual(r['detection_agreement_cases'],1);self.assertEqual(len(r['cases']),3)
 def test_no_recall_denominator_is_unknown_not_zero(self):
  r=m.summarize([[row('C',0,control=True)]]*3);self.assertIsNone(r['recall_pct'])
 def test_different_case_sets_refused(self):
  r=runs();r[1].pop()
  with self.assertRaises(ValueError):m.summarize(r)
 def test_three_runs_required(self):
  with self.assertRaises(ValueError):m.summarize(runs()[:2])
 def test_denominator_drift_refused(self):
  r=runs();r[1][0]['planted']=2
  with self.assertRaises(ValueError):m.summarize(r)
 def test_invalid_reports_never_count_as_agreement(self):
  r=runs()
  for one in r:one[0]['parse_error']=True
  self.assertFalse(m.summarize(r)['cases'][0]['detection_agreement'])
if __name__=='__main__':unittest.main()
