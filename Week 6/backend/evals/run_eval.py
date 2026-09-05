import json
import time
import requests
from pathlib import Path

EVAL_FILE = Path(__file__).parent / "cases.json"
API_URL = "http://localhost:8000/triage"

with open(EVAL_FILE, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

print(f"--- Running Evaluation Benchmark ({len(test_cases)} cases) ---")
passed = 0
results = []

for case in test_cases:
    payload = {"text": case["input"]}
    try:
        res = requests.post(API_URL, json=payload, timeout=35)
        if res.status_code == 200:
            data = res.json()
            actual_category = data.get("category")
            is_match = (actual_category == case["expected_category"])
            if is_match:
                passed += 1
                status = "PASS"
            else:
                status = "FAIL"
            print(f"[{status}] Case #{case['id']} ({case['description']}): Expected='{case['expected_category']}', Actual='{actual_category}' (Confidence: {data.get('confidence')})")
            results.append({
                "id": case["id"],
                "input": case["input"],
                "expected": case["expected_category"],
                "actual": actual_category,
                "passed": is_match,
                "reason": data.get("reason")
            })
        else:
            print(f"[FAIL] Case #{case['id']}: HTTP error {res.status_code}")
            results.append({"id": case["id"], "passed": False, "error": f"HTTP {res.status_code}"})
    except Exception as exc:
        print(f"[ERROR] Case #{case['id']}: {exc}")
        results.append({"id": case["id"], "passed": False, "error": str(exc)})
    time.sleep(0.5)

accuracy = (passed / len(test_cases)) * 100
print(f"\n==========================================")
print(f"Evaluation Summary: {passed}/{len(test_cases)} passed ({accuracy:.1f}%)")
print(f"==========================================")

summary_file = Path(__file__).parent / "eval_results.json"
with open(summary_file, "w", encoding="utf-8") as f:
    json.dump({"passed": passed, "total": len(test_cases), "accuracy_pct": accuracy, "cases": results}, f, indent=2)
