# src/vidhi_lang/generator.py
import sys
import yaml
from pathlib import Path
from typing import List, Type, TypeVar

from pydantic import BaseModel, ValidationError

from vidhi_lang.models import (
    DataCategoriesFile,
    LegalBasisFile,
    ActivitiesFile,
    Obligation,
    ConflictType,
)

T = TypeVar("T", bound=BaseModel)

# ---------------------------------------------------------------------------
# Validating loaders
# ---------------------------------------------------------------------------


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def _validate(path: str, model: Type[T], raw) -> T:
    """Validate raw YAML data against a Pydantic model, with a clean error."""
    try:
        return model.model_validate(raw)
    except ValidationError as e:
        # Re-raise as a flat, user-facing error rather than a Pydantic stack.
        raise SystemExit(
            f"\n[vidhi-lang] Validation failed in {path}:\n{e}\n"
        )

def _validate_list(path: str, model: Type[T], raw) -> List[T]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SystemExit(
            f"\n[vidhi-lang] {path} must be a YAML list at the top level.\n"
        )
    out = []
    for i, item in enumerate(raw):
        try:
            out.append(model.model_validate(item))
        except ValidationError as e:
            raise SystemExit(
                f"\n[vidhi-lang] Validation failed in {path} (item {i}):\n{e}\n"
            )
    return out


def load_all(paths):
    items = []
    for p in paths:
        data = load_yaml(p) or []
        items.extend(data)
    return items


def load_activities(path):
    raw = load_yaml(path) or []
    if raw is None:
        return []
    return _validate(path, ActivitiesFile, raw).activities


def load_data_categories(path):
    return _validate(path, DataCategoriesFile, load_yaml(path)).categories


def load_legal_basis(path):
    return _validate(path, LegalBasisFile, load_yaml(path)).legal_bases


def load_obligations(paths):
    out = []
    for p in paths:
        out.extend(_validate_list(p, Obligation, load_yaml(p)))
    return out

def load_conflicts(paths):
    out = []
    for p in paths:
        out.extend(_validate_list(p, ConflictType, load_yaml(p)))
    return out



def get_activity(activity_id, activities):
    for a in activities:
        if a["id"] == activity_id:
            return a
    return None


def filter_obligations_by_domain(activity, obligations):
    if activity.startswith("insurance."):
        return [o for o in obligations if o["id"].startswith(("irdai.", "dpdp."))]
    elif activity.startswith("banking."):
        return [o for o in obligations if o["id"].startswith(("rbi.", "dpdp."))]
    return obligations


def matches(data_used, applies_to):
    for d in data_used:
        for a in applies_to:
            if d.startswith(a):
                return True
    return False


def detect_conflicts(obligations, conflicts):
    result = []

    has_retain = any("retain" in o for o in obligations)
    has_erase = any("erase" in o for o in obligations)

    if has_retain and has_erase:
        for c in conflicts:
            if c["id"] == "retention_vs_erasure":
                result.append(c["id"])

    return result


def generate(manifest_path, obligations_paths, conflicts_paths, activities_path,data_categories_path=None,legal_basis_path=None,):
    
    if data_categories_path:
        load_data_categories(data_categories_path) 
    
    if legal_basis_path:
        load_legal_basis(legal_basis_path)  # validate-only for now


    activities_models = load_activities(activities_path)
    obligations_models = load_obligations(obligations_paths)
    conflicts_models = load_conflicts(conflicts_paths)

    activities = [a.model_dump() for a in activities_models]
    obligations = [o.model_dump() for o in obligations_models]
    conflicts = [c.model_dump() for c in conflicts_models]

    
    manifest = load_yaml(manifest_path) or {}
    activity = manifest.get("activity", "")
    activity_def = get_activity(activity, activities)

    # --- Filter obligations by domain ---
    obligations = filter_obligations_by_domain(activity, obligations)

    data_used = manifest.get("data_used")
    legal_basis = manifest.get("legal_basis")

    if activity_def:
        if not data_used:
            data_used = activity_def.get("typical_data_categories", [])
        if not legal_basis:
            legal_basis = activity_def.get("typical_legal_basis", [])

    data_used = data_used or []
    legal_basis = legal_basis or []

    # --- Build output ---
    output = {
        "activity": activity,
        "data_subjects": manifest.get("data_subjects", []),
        "data_categories": data_used,
        "legal_basis": legal_basis,
        "obligations": [],
        "potential_conflicts": []
    }

    # --- Match obligations ---
    for o in obligations:
        if matches(data_used, o.get("applies_to", [])):
            output["obligations"].append(o["id"])

    # --- Detect conflicts ---
    output["potential_conflicts"] = detect_conflicts(
        output["obligations"], conflicts
    )

    return output