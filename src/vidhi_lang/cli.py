# src/vidhi_lang/cli.py

import sys
import json
from pathlib import Path
from vidhi_lang.generator import generate

def main(manifest_path):
    if len(sys.argv) < 2:
        print("Usage: python -m vidhi_lang.cli <manifest.yaml>")
        return

    
    manifest_path = sys.argv[1]

    project_root = Path(__file__).resolve().parent.parent.parent

    obligations_paths = sorted(str(p) for p in (project_root / "obligations").glob("*.yaml"))
    conflicts_paths = sorted(str(p) for p in (project_root / "conflicts").glob("*.yaml"))
    activities_path = project_root / "taxonomies" / "processing_activities.yaml"
    data_categories_path = project_root / "taxonomies" / "data_categories.yaml"
    legal_basis_path = project_root / "taxonomies" / "legal_basis.yaml"


    result = generate(
        manifest_path,
        obligations_paths,
        conflicts_paths,
        str(activities_path),
        str(data_categories_path),
        str(legal_basis_path),

    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()