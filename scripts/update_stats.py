import json
import re
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]

method_dir = repo_root / "docs/methods"
dataset_dir = repo_root / "docs/datasets"
commercial_file = repo_root / "docs/commercial.md"
agentic_file = method_dir / "agentic-ai.md"


def table_rows(file, first_column):
    """Yield records only from tables with the requested first-column header."""
    header = None
    for line in file.read_text().splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            header = None
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if header is None:
            header = cells
            continue
        if header[0] == first_column:
            yield cells


def count_table_rows(file, first_column="Model"):
    return sum(1 for _ in table_rows(file, first_column))


def count_models():
    # Every method category uses Model rows, including Agentic AI.
    return sum(count_table_rows(f) for f in method_dir.glob("*.md"))


def count_datasets():
    total = 0
    for f in dataset_dir.glob("*.md"):
        total += count_table_rows(f, "Dataset")
    return total


def count_commercial():
    models = []
    for cells in table_rows(commercial_file, "Family"):
        for entry in cells[2].split("<br>"):
            entry = entry.strip()
            if entry and entry != "—":
                name = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", entry)
                models.append(name.casefold())
    if len(models) != len(set(models)):
        raise RuntimeError("Duplicate current model in docs/commercial.md")
    return len(models)


def main():
    stats = {
        "models": count_models(),
        "datasets": count_datasets(),
        "commercial_models": count_commercial(),
        "agentic_ai": count_table_rows(agentic_file),
    }
    output = repo_root / "docs/stats.json"
    output.write_text(json.dumps(stats, indent=2) + "\n")
    print("Updated stats:", stats)


if __name__ == "__main__":
    main()
