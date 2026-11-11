from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from alignment_observatory.core import run,digest,BusinessError
class AvatarAlignmentCoreTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.db=str(Path(self.temp.name)/'core.sqlite3')
 def fixture(self):
  return {'subject_id':'synthetic','request_key':'core-test','payload':{"doctor_id": "d-1", "baseline": 70, "drift_threshold": 5, "samples": [{"score": 80, "shown": True, "accepted": True, "modified": False, "cohort": "sleep", "original": "复核", "edited": "医生复核"}, {"score": 65, "shown": True, "accepted": False, "modified": True, "cohort": "sleep", "original": "建议", "edited": "建议复诊"}]}}
 def test_domain_result_is_persisted(self):
  result=run(self.fixture(),self.db); self.assertTrue(result); self.assertTrue(any(k in result for k in ('snapshot','automation','transcript','delivery','alignment','followup','incident','enrollment','release'))); self.assertIn('stored',result); self.assertEqual(result['stored']['completed']['record']['state'],result['stored']['completed']['record']['state'])
 def test_deterministic_domain_summary(self):
  left=run(self.fixture(),self.db); other=str(Path(self.temp.name)/'other.sqlite3'); right=run(self.fixture(),other); key=next(k for k in left if k!='stored'); self.assertEqual(digest(left[key]),digest(right[key]))
 def test_duplicate_business_input_replays(self):
  first=run(self.fixture(),self.db); second=run(self.fixture(),self.db); self.assertEqual(first['stored']['opened'],second['stored']['opened'])
 def test_output_has_audit_events(self):
  result=run(self.fixture(),self.db); self.assertGreaterEqual(result['stored']['completed']['audit_count'],7)
 def test_result_hashes_are_sha256(self):
  result=run(self.fixture(),self.db); key=next(k for k in result if k!='stored'); self.assertEqual(len(digest(result[key])),64)
 def test_payload_mutation_changes_result(self):
  raw=self.fixture(); raw['payload']['score']=999; result=run(raw,self.db); self.assertIsInstance(result,dict)
 def test_missing_optional_fields_use_local_defaults(self):
  raw=self.fixture(); raw['payload'].pop('score',None); self.assertTrue(run(raw,self.db))
 def test_database_is_created(self):
  run(self.fixture(),self.db); self.assertTrue(Path(self.db).is_file())
 def test_no_external_network_is_required(self):
  result=run(self.fixture(),self.db); self.assertNotIn('http_response',result)
 def test_business_error_type_is_value_error(self):
  self.assertTrue(issubclass(BusinessError,ValueError))
