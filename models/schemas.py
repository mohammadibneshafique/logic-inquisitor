"""
models/schemas.py
All Pydantic models for The Logic Inquisitor.
Type-safe contracts between every agent in the pipeline.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ─── Submission Record (Archivist memory) ─────────────────────────────────────

class SubmissionRecord(BaseModel):
    id: str
    timestamp: float
    language: str
    bug_type: str
    problem_category: str
    complexity_tier: str


# ─── Agent 2: Linguist ────────────────────────────────────────────────────────

class CodeQualitySignal(BaseModel):
    signal: str
    severity: str  # low | medium | high


class LinguistOutput(BaseModel):
    language: str
    confidence: float = Field(ge=0.0, le=1.0)
    framework: Optional[str] = None
    runtime: Optional[str] = None
    input_type: str  # code | error_log | description | mixed
    code_quality_signals: list[CodeQualitySignal] = Field(default_factory=list)
    reasoning: str


# ─── Agent 3: Pathologist ─────────────────────────────────────────────────────

class SeverityMatrix(BaseModel):
    impact: int = Field(ge=1, le=5)
    frequency: int = Field(ge=1, le=5)
    detectability: int = Field(ge=1, le=5)
    overall: str  # low | medium | high | critical


class PathologistOutput(BaseModel):
    bug_type: str
    problem_category: str
    complexity_tier: str  # beginner | intermediate | advanced | expert
    conceptual_gap: str
    affected_region: Optional[str] = None
    severity: SeverityMatrix
    reasoning: str


# ─── Agent 4: Socrates ────────────────────────────────────────────────────────

class SocratesOutput(BaseModel):
    tier1: str
    tier2: str
    tier3: str
    concept_url: str
    concept_name: str
    current_tier: int = 1


# ─── Agent 5: Archivist ───────────────────────────────────────────────────────

class PatternCard(BaseModel):
    concept: str
    occurrences: int
    severity: str  # mild | moderate | persistent
    study_resource: str
    study_url: str


class ArchivistOutput(BaseModel):
    submission_count: int
    pattern_cards: list[PatternCard] = Field(default_factory=list)
    learning_profile: Optional[str] = None
    recurring_bug_types: list[dict] = Field(default_factory=list)
    recommended_topics: list[str] = Field(default_factory=list)


# ─── Master State (LangGraph shared state) ────────────────────────────────────

class InquisitorState(BaseModel):
    raw_input: str
    session_id: str
    session_history: list[SubmissionRecord] = Field(default_factory=list)
    linguist_output: Optional[LinguistOutput] = None
    pathologist_output: Optional[PathologistOutput] = None
    socrates_output: Optional[SocratesOutput] = None
    archivist_output: Optional[ArchivistOutput] = None
    current_hint_tier: int = 1
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
