"""Script to run POC on all test samples and generate reports."""

import json
import sys
from pathlib import Path

# Add parent directory to path to import ast_diff_poc
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ast_diff_poc.diff.diff_engine import DiffEngine
from ast_diff_poc.utils.file_loader import load_property_file


def run_poc_on_samples():
    """Run POC on all sample files."""
    base_dir = Path(__file__).parent.parent
    fixtures_dir = base_dir / "tests" / "fixtures"
    output_dir = base_dir / "output"

    output_dir.mkdir(exist_ok=True)

    engine = DiffEngine()
    results = {}

    for sample_num in range(1, 6):
        sample_dir = fixtures_dir / f"sample{sample_num}"
        source_file = sample_dir / "source.properties"
        target_file = sample_dir / "target.properties"

        if not source_file.exists() or not target_file.exists():
            print(f"Warning: Sample {sample_num} files not found, skipping...")
            continue

        print(f"Processing sample {sample_num}...")

        try:
            source_ast = load_property_file(str(source_file))
            target_ast = load_property_file(str(target_file))

            result = engine.compute_diff(source_ast, target_ast)
            result_dict = result.to_dict()

            # Save individual result
            output_file = output_dir / f"sample{sample_num}_result.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            results[f"sample{sample_num}"] = result_dict

            print(f"  ✓ Processed: {len(result.changes)} changes detected")
            print(f"    Summary: {result.summary.added} added, "
                  f"{result.summary.deleted} deleted, "
                  f"{result.summary.modified} modified, "
                  f"{result.summary.moved} moved, "
                  f"{result.summary.moved_and_modified} moved+modified")

        except Exception as e:
            print(f"  ✗ Error processing sample {sample_num}: {e}")
            results[f"sample{sample_num}"] = {"error": str(e)}

    # Save combined results
    combined_output = output_dir / "all_results.json"
    with open(combined_output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nAll results saved to {output_dir}")
    return results


if __name__ == "__main__":
    run_poc_on_samples()
