from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    KPI = "kpi_definition"
    FUNNEL = "funnel"
    SEGMENT = "segmentation"
    EXPERIMENT = "experiment"


class AnalysisPlan(BaseModel):
    analysis_type: AnalysisType
    metric: str = "activation_rate"
    dimension: str | None = None
    filters: dict[str, str] = Field(default_factory=dict)
    rationale: str


class AnalysisResult(BaseModel):
    analysis_type: AnalysisType
    title: str
    summary: dict[str, Any]
    table: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
