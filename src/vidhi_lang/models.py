from pydantic import BaseModel, Field
from typing import List, Literal

Sensitivity = Literal[
    "non_personal",
    "personal",
    "sensitive_personal",
    "health",
    "child"
]

# Dot-notation IDs used for data categories, activities, and obligations.
#Pattern: <segment>.<segment>.<segment> — lowercase, underscores allowed
DOT_ID_PATTERN = r"^[a-z]+\.[a-z]+\.[a-z_]+$"

# Snake-case IDs used for legal bases (e.g. consent, legal_obligation).
SNAKE_ID_PATTERN = r"^[a-z][a-z_]*$"


# Conflict-type IDs use <concept>_vs_<concept>.
CONFLICT_ID_PATTERN = r"^[a-z][a-z_]*_vs_[a-z][a-z_]*$"


class DataCategory(BaseModel):
    id: str = Field(..., pattern=DOT_ID_PATTERN)
    name: str
    description: str
    sensitivity: Sensitivity

class DataCategoriesFile(BaseModel):
    version: str
    categories: List[DataCategory]


class Obligation(BaseModel):
    id: str = Field(..., pattern=DOT_ID_PATTERN)
    description: str
    applies_to: List[str] = []


class LegalBasis(BaseModel):
    id: str = Field(..., pattern=SNAKE_ID_PATTERN)
    name: str
    description: str

class LegalBasisFile(BaseModel):
    version: str
    legal_bases: List[LegalBasis]


class ConflictType(BaseModel):
    id: str = Field(..., pattern=CONFLICT_ID_PATTERN)
    description: str



class Activity(BaseModel):
    id: str = Field(..., pattern=DOT_ID_PATTERN)
    name: str
    description: str
    data_categories: List[str] = []
    legal_basis: List[str] = []


class ActivitiesFile(BaseModel):
    version: str
    activities: List[Activity]
