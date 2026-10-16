#!/usr/bin/env python3
"""Offline descriptive variance of pinned published reports. No model requests."""
import argparse,hashlib,io,json,subprocess,tarfile,tempfile
from pathlib import Path
SOURCE='96641b8ce3c3ced4be25399a9758a632d09b268c'
HISTORICAL='13b4f3144d740b2825db4b55af55e40c8ab1baa7'
def spread(values):
 return dict(values=values,min=min(values),max=max(values),spread=max(values)-min(values))
def summarize(runs):
 if len(runs)!=3:raise ValueError('exactly three runs required')
 indexed=[{r['id']:r for r in run} for run in runs]
 if any(len(i)!=len(r) for i,r in zip(indexed,runs)) or any(set(i)!=set(indexed[0]) for i in indexed):raise ValueError('case sets differ or duplicate IDs')
 cases=[]
 for identity in sorted(indexed[0]):
  rows=[i[identity] for i in indexed]
  if len({(r['control'],r['planted']) for r in rows})!=1:raise ValueError('denominator drift')
  valid=not any(r['parse_error'] for r in rows)
  cases.append(dict(id=identity,control=rows[0]['control'],planted=rows[0]['planted'],recall_hits=[r['recall_hits'] for r in rows],false_alarms=[r['false_alarm'] for r in rows],verdicts=[r['verdict'] for r in rows],invalid=[r['parse_error'] for r in rows],detection_agreement=valid and len({r['signature'] for r in rows})==1,verdict_agreement=valid and len({r['verdict'] for r in rows})==1))
 planted=sum(r['planted'] for r in runs[0])
 return dict(cases_per_run=len(cases),controls_per_run=sum(r['control'] for r in runs[0]),planted_per_run=planted,recall_hits=spread([sum(r['recall_hits'] for r in run) for run in runs]),recall_pct=spread([100*sum(r['recall_hits'] for r in run)/planted for run in runs]) if planted else None,false_alarms=spread([sum(r['false_alarm'] for r in run if r['control']) for run in runs]),detection_agreement_cases=sum(c['detection_agreement'] for c in cases),verdict_agreement_cases=sum(c['verdict_agreement'] for c in cases),cases=cases)
def archive(repo,commit,dest,paths):
 raw=subprocess.check_output(['git','-C',str(repo),'archive',commit,*paths])
 with tarfile.open(fileobj=io.BytesIO(raw)) as tar:tar.extractall(dest,filter='data')
def build(repo):
 manifest=[];cohorts={}
 with tempfile.TemporaryDirectory() as directory:
  root=Path(directory);current=root/'current';old=root/'old';current.mkdir();old.mkdir()
  archive(repo,SOURCE,current,['evals','tools','schema'])
  archive(repo,HISTORICAL,old,['evals/score.py','evals/score_assess.py','evals/cases','evals/holdout/cases','tools','schema'])
  configs=[('redteam-dev','2026-10-09-gate-v232/dev-v232-',old/'evals/cases',False),('redteam-holdout','2026-10-09-gate-v232/ho-v232-',old/'evals/holdout/cases',False),('pr-review-controls','2026-10-08-prreview-held/prreview-v22-',old/'evals/cases',False),('assess-corrected','2026-10-09-assess-holdout3/holdout3-v13-',current/'evals/assess/holdout3/cases',True)]
  for name,prefix,cases,assess in configs:
   runs=[];totals=[]
   for n in range(1,4):
    reports=current/'evals/results'/f'{prefix}{n}';out=root/f'{name}-{n}.json';scorer=current/'evals/score_assess.py' if assess else old/'evals/score.py'
    cmd=['python3',str(scorer),'--cases',str(cases),'--reports',str(reports),'--json',str(out)]
    if not assess:cmd+=['--skill','pr-review' if name=='pr-review-controls' else 'redteam','--profile','v2.3']
    if name=='pr-review-controls':cmd+=['--only','case-35,case-36']
    result=subprocess.run(cmd,capture_output=True)
    if not out.exists():raise RuntimeError('offline scorer failed: '+name)
    data=json.loads(out.read_text());totals.append(data['totals']);rows=[]
    for c in data['cases']:
     if assess:
      rows.append(dict(id=c['id'],control=c['control'],planted=0,recall_hits=0,false_alarm=int(c['control'] and not c['pass']),verdict='PASS' if c['pass'] else 'FAIL',parse_error=bool(c['schema']),signature=json.dumps([c['pass'],c['failed'],c['schema']],sort_keys=True)))
     else:
      rows.append(dict(id=c['id'],control=c['control'],planted=c['planted'],recall_hits=c['recall_hits'],false_alarm=c['false_alarm'],verdict=c['verdict'],parse_error=c['verdict'] is None,signature=json.dumps([c['missed'],c['low_severity'],c['false_alarm']],sort_keys=True)))
    runs.append(rows)
    for path in sorted(reports.rglob('*.md')):manifest.append(dict(path=str(path.relative_to(current)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
   summary=summarize(runs);summary['scorer_totals']=totals
   if assess:
    summary['agreement_metric']='case pass/fail and failed rule identity, corrected scorer; not defect recall'
    summary['case_passes']=spread([sum(c['verdict']=='PASS' for c in run) for run in runs]);summary['published_as_run_case_passes']=[36,35,35];summary['recall_pct']=None
   else:summary['agreement_metric']='same planted items missed or downgraded and same control alarm count; not identical prose or extra findings'
   cohorts[name]=summary
  scorers=[dict(path='evals/score.py',commit=HISTORICAL,sha256=hashlib.sha256((old/'evals/score.py').read_bytes()).hexdigest()),dict(path='evals/score_assess.py',commit=SOURCE,sha256=hashlib.sha256((current/'evals/score_assess.py').read_bytes()).hexdigest())]
 return dict(schema='published-variance-1',source_commit=SOURCE,new_model_runs=0,redteam_scorer_commit=HISTORICAL,redteam_profile='v2.3',cohorts=cohorts,scorers=scorers,published_report_hashes=manifest)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.write_text(json.dumps(build(a.source),indent=2)+'\n')
if __name__=='__main__':main()
