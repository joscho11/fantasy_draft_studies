"""Execute generated notebook code cells without requiring Jupyter."""
from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
requested = set(sys.argv[1:])
paths = sorted((ROOT / "notebooks").glob("*.ipynb"))
if requested:
    paths = [path for path in paths if path.name in requested or path.stem in requested]

for path in paths:
    namespace = {"__name__": "__main__"}
    notebook = json.loads(path.read_text(encoding="utf-8"))
    print(f"Running {path.name}")
    cells = notebook["cells"]
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        first_line = "".join(cell["source"]).splitlines()[0] if cell.get("source") else "<empty>"
        print(f"  {first_line}")
        namespace["_SECTION_INTERPRETATION"] = None
        charts_before = len(namespace.get("_CHART_FILES", []))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exec("".join(cell["source"]), namespace)
        outputs = []
        printed = buffer.getvalue()
        if printed:
            outputs.append({"name": "stdout", "output_type": "stream", "text": printed.splitlines(True)})
        for filename in namespace.get("_CHART_FILES", [])[charts_before:]:
            html = (ROOT / "artifacts" / filename).read_text(encoding="utf-8")
            outputs.append({
                "data": {"text/html": [html], "text/plain": [f"<Chart: {filename}>"]},
                "metadata": {},
                "output_type": "display_data",
            })
        cell["outputs"] = outputs
        cell["execution_count"] = 1
        interpretation = namespace.get("_SECTION_INTERPRETATION")
        if interpretation and index + 1 < len(cells):
            following = cells[index + 1]
            if following.get("metadata", {}).get("role") == "interpretation":
                following["source"] = [f"### Interpretation\n\n{interpretation.strip()}\n"]
    path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
