# examples/app/backend/app.py
#
# Sample FastAPI app demonstrating vidhi-lang in a web context.
# Shows how a product (e.g. Complianx) might wrap the standard.
#
# Run:
#   pip install fastapi uvicorn pyyaml pydantic
#   PYTHONPATH=src uvicorn examples.app.backend.app:app --reload --port 8000

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import List
import tempfile, yaml, os

from vidhi_lang.generator import generate

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="vidhi-lang Sample API",
    description="Demonstrates vidhi-lang RoPA generation over HTTP.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def _vocab_paths():
    return dict(
        obligations_paths=sorted(
            str(p) for p in (PROJECT_ROOT / "obligations").glob("*.yaml")
        ),
        conflicts_paths=sorted(
            str(p) for p in (PROJECT_ROOT / "conflicts").glob("*.yaml")
        ),
        activities_path=str(PROJECT_ROOT / "taxonomies" / "processing_activities.yaml"),
        data_categories_path=str(PROJECT_ROOT / "taxonomies" / "data_categories.yaml"),
        legal_bases_path=str(PROJECT_ROOT / "taxonomies" / "legal_bases.yaml"),
    )

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ManifestRequest(BaseModel):
    activity: str
    data_subjects: List[str] = []
    data_used: List[str] = []
    legal_basis: List[str] = []
    source_tables: List[str] = []

class ActivitySummary(BaseModel):
    id: str
    name: str
    description: str
    data_categories: List[str]
    legal_basis: List[str]

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "version": "0.3.0", "standard": "vidhi-lang"}


@app.get("/activities", response_model=List[ActivitySummary], tags=["vocabulary"])
def list_activities():
    """Return all known processing activities from the taxonomy."""
    from vidhi_lang.generator import load_activities
    acts = load_activities(_vocab_paths()["activities_path"])
    return [ActivitySummary(**a.model_dump()) for a in acts]


@app.get("/obligations", tags=["vocabulary"])
def list_obligations():
    """Return all obligations across all regulators."""
    from vidhi_lang.generator import load_obligations
    obs = load_obligations(_vocab_paths()["obligations_paths"])
    return [o.model_dump() for o in obs]


@app.get("/data-categories", tags=["vocabulary"])
def list_data_categories():
    """Return all data categories from the taxonomy."""
    from vidhi_lang.generator import load_data_categories
    cats = load_data_categories(_vocab_paths()["data_categories_path"])
    return [c.model_dump() for c in cats]


@app.post("/generate", tags=["ropa"])
def generate_ropa(manifest: ManifestRequest):
    """
    Generate a RoPA entry from a manifest payload.

    Fields are optional — omit data_used or legal_basis to trigger
    autofill from the activity taxonomy.
    """
    raw = manifest.model_dump(exclude_none=True)

    # Write to a temp YAML file — generator expects a file path today.
    # This wiring will be replaced once generator accepts dict input (v0.4).
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    )
    try:
        yaml.safe_dump(raw, tmp)
        tmp.close()
        v = _vocab_paths()
        result = generate(
            tmp.name,
            v["obligations_paths"],
            v["conflicts_paths"],
            v["activities_path"],
            v["data_categories_path"],
            v["legal_bases_path"],
        )
    except SystemExit as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp.name)

    return result
