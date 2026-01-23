"""Command-line interface for AST Diff POC."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .diff.diff_engine import DiffEngine
from .utils.file_loader import load_property_file


@click.command()
@click.argument("source_file", type=click.Path(exists=True, path_type=Path))
@click.argument("target_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--no-normalize",
    is_flag=True,
    help="Disable AST normalization before comparison",
)
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty-print JSON output",
)
@click.option(
    "--no-complexity",
    is_flag=True,
    help="Disable complexity calculation",
)
def main(
    source_file: Path,
    target_file: Path,
    output: Optional[Path],
    no_normalize: bool,
    pretty: bool,
    no_complexity: bool,
) -> None:
    """Compute AST-based diff between two property files.

    SOURCE_FILE: Path to the source property file
    TARGET_FILE: Path to the target property file
    """
    try:
        # Load files
        source_ast = load_property_file(str(source_file))
        target_ast = load_property_file(str(target_file))

        # Compute diff
        engine = DiffEngine(normalize=not no_normalize, calculate_complexity=not no_complexity)
        result = engine.compute_diff(source_ast, target_ast)

        # Convert to dict (exclude complexity for diff output)
        output_dict = result.to_dict(exclude_complexity=True)

        # Output
        json_str = json.dumps(output_dict, indent=2 if pretty else None)

        if output:
            output.write_text(json_str, encoding="utf-8")
            click.echo(f"Diff result written to {output}")
        else:
            click.echo(json_str)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
