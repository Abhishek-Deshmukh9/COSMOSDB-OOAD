from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT / "docs" / "OOAD" / "diagrams"
DIAGRAMS = sorted(DIAGRAM_DIR.glob("*.puml"))


def main() -> int:
    if not DIAGRAMS:
        print(f"No PlantUML files found under {DIAGRAM_DIR}.", file=sys.stderr)
        return 2

    java = shutil.which("java")
    graphviz = shutil.which("dot")
    jar_path = os.getenv("PLANTUML_JAR")
    plantuml = shutil.which("plantuml")
    if not java:
        print("Java was not found. Install a supported JRE and retry.", file=sys.stderr)
        return 2
    if not graphviz:
        print("Graphviz 'dot' was not found; PlantUML may use its built-in layout engine.", file=sys.stderr)

    if jar_path:
        jar = Path(jar_path)
        if not jar.is_file():
            print(f"PLANTUML_JAR does not point to a file: {jar}", file=sys.stderr)
            return 2
        command = [java, "-jar", str(jar), "-tsvg", *map(str, DIAGRAMS)]
    elif plantuml:
        command = [plantuml, "-tsvg", *map(str, DIAGRAMS)]
    else:
        print(
            "PlantUML was not found. Install PlantUML or set PLANTUML_JAR to a local plantuml.jar.",
            file=sys.stderr,
        )
        return 2

    result = subprocess.run(command, cwd=DIAGRAM_DIR, check=False)
    if result.returncode:
        return result.returncode
    missing = [path.with_suffix(".svg") for path in DIAGRAMS if not path.with_suffix(".svg").is_file()]
    if missing:
        print("PlantUML exited successfully but did not create: " + ", ".join(map(str, missing)), file=sys.stderr)
        return 1
    print(f"Rendered {len(DIAGRAMS)} diagrams to SVG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
