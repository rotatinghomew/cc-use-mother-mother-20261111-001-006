from __future__ import annotations
import hashlib,json,re
from collections import defaultdict,deque
from typing import Any,Mapping
def stable(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(v): return hashlib.sha256(stable(v).encode()).hexdigest()
class BusinessError(ValueError): pass

from alignment_observatory.registry.sqlite_registry import process_fixture
def distance(a,b):
 prev=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  cur=[i]
  for j,y in enumerate(b,1): cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
  prev=cur
 return prev[-1]
def run(raw,database):
 p=raw.get('payload',raw); rows=[dict(x) for x in p.get('samples',[])]; shown=sum(bool(x.get('shown',True)) for x in rows); accepted=sum(bool(x.get('accepted')) for x in rows); modified=sum(bool(x.get('modified')) for x in rows)
 scores=[float(x.get('score',0)) for x in rows]; mean=sum(scores)/len(scores) if scores else 0.0; baseline=float(p.get('baseline',mean)); edits=[distance(str(x.get('original','')),str(x.get('edited',''))) for x in rows]
 result={'count':len(rows),'adoption_rate':accepted/shown if shown else 0.0,'modified_rate':modified/shown if shown else 0.0,'coverage':sum(x.get('score') is not None for x in rows)/len(rows) if rows else 0.0,'mean_score':mean,'edit_distances':edits,'drift':mean-baseline,'alert':abs(mean-baseline)>float(p.get('drift_threshold',10)),'cohorts':sorted({str(x.get('cohort','default')) for x in rows})}
 stored=process_fixture(database,{'subject_id':str(p.get('doctor_id','doctor-demo')),'request_key':digest(result),'payload':result})
 return {'alignment':result,'stored':stored}
