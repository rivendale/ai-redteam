Rework: R-7 allows at most 180 days in staging, so 400 is out.
```json
{"verdict": "Rework", "findings": [{"id": "R1", "severity": "high", "evidence": "confirmed", "location": {"file": "work/change.md", "line": 3}, "issue": "R-7 caps non-production retention at 180 days; the change asks for 400", "failure_scenario": "R-7 caps non-production retention at 180 days; the change asks for 400", "recommendation": "R-7 caps non-production retention at 180 days; the change asks for 400"}], "ledger": {"read": ["all"], "not_read": []}}
```
