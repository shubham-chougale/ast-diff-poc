"""Script to generate test result summaries."""

import json
from pathlib import Path
from typing import Dict, Any


def generate_summary_report():
    """Generate a summary report of all test results."""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"
    results_file = output_dir / "all_results.json"

    if not results_file.exists():
        print("Error: No results file found. Run run_poc.py first.")
        return

    with open(results_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    summary = {
        "total_samples": len(results),
        "samples": {},
    }

    for sample_name, result in results.items():
        if "error" in result:
            summary["samples"][sample_name] = {"status": "error", "error": result["error"]}
            continue

        sample_summary = result.get("summary", {})
        summary["samples"][sample_name] = {
            "status": "success",
            "total_changes": len(result.get("changes", [])),
            "added": sample_summary.get("added", 0),
            "deleted": sample_summary.get("deleted", 0),
            "modified": sample_summary.get("modified", 0),
            "moved": sample_summary.get("moved", 0),
            "moved_and_modified": sample_summary.get("moved_and_modified", 0),
        }

    # Save summary
    summary_file = output_dir / "summary_report.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Print summary
    print("=" * 60)
    print("AST Diff POC - Test Results Summary")
    print("=" * 60)
    print(f"\nTotal Samples Processed: {summary['total_samples']}\n")

    for sample_name, sample_data in summary["samples"].items():
        print(f"{sample_name.upper()}:")
        if sample_data["status"] == "error":
            print(f"  Status: ERROR - {sample_data['error']}")
        else:
            print(f"  Status: SUCCESS")
            print(f"  Total Changes: {sample_data['total_changes']}")
            print(f"    - Added: {sample_data['added']}")
            print(f"    - Deleted: {sample_data['deleted']}")
            print(f"    - Modified: {sample_data['modified']}")
            print(f"    - Moved: {sample_data['moved']}")
            print(f"    - Moved & Modified: {sample_data['moved_and_modified']}")
        print()

    print(f"\nDetailed results saved to: {output_dir}")
    print(f"Summary report saved to: {summary_file}")


if __name__ == "__main__":
    generate_summary_report()
