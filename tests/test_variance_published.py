#!/usr/bin/env python3
"""Reconcile profiles and historical tallies against pinned published data, offline."""
import argparse,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('variance',ROOT/'tools/report_variance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path);a=p.parse_args();actual=m.build(a.source);c=actual['cohorts']
 assert [r['violations'] for r in c['pr-review-controls']['scorer_totals']]==[0,0,0], 'pr-review profile differs from published result'
 assert c['assess-as-run']['case_passes']['values']==[36,35,35]
 assert c['assess-as-run']['detection_agreement_cases']==34
 assert c['assess-corrected']['case_passes']['values']==[36,36,36]
 assert actual==json.loads((ROOT/'docs/variance-2026-10-16.json').read_text()),'committed report differs from regeneration'
 print('Published profiles, original/corrected assess tallies and exact report regeneration pass; no model runs')
if __name__=='__main__':main()
