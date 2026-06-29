import json
from pathlib import Path

from src.models.schemas import ClassificationResult, VendorInfo, parse_llm_json
from src.prompts.registry import PromptRegistry
from src.providers.base import BaseLLMProvider


TEST_CASES_PATH = Path(__file__).parent / "test_cases.json"


def load_test_cases() -> list[dict]:
    """Load test cases from the JSON file."""
    return json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))


def evaluate_classification(provider: BaseLLMProvider, registry: PromptRegistry) -> dict:
    """Run all test cases through the classification step and score accuracy.

    For each test case:
    1. Build the prompt using the registry
    2. Send it to the LLM
    3. Parse the response into a ClassificationResult
    4. Compare the predicted category against the expected category

    Returns a summary with pass/fail counts and details.
    """
    test_cases = load_test_cases()
    results = []

    for tc in test_cases:
        prompt = registry.get("classify_v1", request_text=tc["input"])

        try:
            response = provider.generate(prompt)
            parsed = parse_llm_json(response.content, ClassificationResult)
            predicted = parsed.category.value
            expected = tc["expected"]["category"]
            passed = predicted == expected

            results.append({
                "id": tc["id"],
                "input": tc["input"][:60] + "...",
                "expected": expected,
                "predicted": predicted,
                "confidence": parsed.confidence,
                "passed": passed,
            })
        except Exception as e:
            results.append({
                "id": tc["id"],
                "input": tc["input"][:60] + "...",
                "expected": tc["expected"]["category"],
                "predicted": None,
                "error": str(e),
                "passed": False,
            })

    passed_count = sum(1 for r in results if r["passed"])

    return {
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "accuracy": round(passed_count / len(results) * 100, 1),
        "details": results,
    }


def print_eval_report(report: dict):
    """Print evaluation results in a readable format."""
    print("\n" + "=" * 60)
    print("  EVALUATION REPORT — Classification")
    print("=" * 60)
    print(f"  Accuracy: {report['accuracy']}% ({report['passed']}/{report['total']})")
    print("-" * 60)

    for r in report["details"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['id']}: {r['input']}")
        if r["passed"]:
            print(f"         → {r['predicted']} (confidence: {r.get('confidence', 'N/A')})")
        elif "error" in r:
            print(f"         → ERROR: {r['error']}")
        else:
            print(f"         → expected '{r['expected']}', got '{r['predicted']}'")

    print("=" * 60)
