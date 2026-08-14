"""Execute code cells in generated notebooks without requiring Jupyter."""
from __future__ import annotations
import json
import sys
import io
from contextlib import redirect_stdout
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
requested=set(sys.argv[1:])
paths=sorted((ROOT/"notebooks").glob("*.ipynb"))
if requested: paths=[path for path in paths if path.name in requested or path.stem in requested]
for path in paths:
    namespace={"__name__":"__main__"}
    notebook=json.loads(path.read_text(encoding="utf-8"))
    print(f"Running {path.name}")
    for cell in notebook["cells"]:
        if cell["cell_type"]=="code":
            charts_before=len(namespace.get("_CHART_FILES",[]))
            buffer=io.StringIO()
            with redirect_stdout(buffer): exec("".join(cell["source"]),namespace)
            outputs=[]
            printed=buffer.getvalue()
            if printed: outputs.append({"name":"stdout","output_type":"stream","text":printed.splitlines(True)})
            for filename in namespace.get("_CHART_FILES",[])[charts_before:]:
                html=(ROOT/"artifacts"/filename).read_text(encoding="utf-8")
                outputs.append({"data":{"text/html":[html],"text/plain":[f"<Chart: {filename}>"]},"metadata":{},"output_type":"display_data"})
            cell["outputs"]=outputs; cell["execution_count"]=1
    path.write_text(json.dumps(notebook,indent=1),encoding="utf-8")

from refresh_interpretations import refresh
refresh(ROOT)
