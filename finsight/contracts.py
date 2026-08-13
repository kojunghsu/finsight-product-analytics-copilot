from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    KPI = "kpi_definition"
    FUNNEL = "funnel"
    SEGMENT = "segmentation"
    ENGAGEMENT = "engagement_spend"
    RETENTION = "retention_inactivity"
    EXPERIMENT = "experiment"
    UNSUPPORTED = "unsupported"


class FilterClause(BaseModel):
    column: Literal["device", "acquisition_channel", "customer_segment", "experiment_group"]
    value: str


class AnalysisPlan(BaseModel):
    analysis_type: AnalysisType
    metric: str
    dimension: str | None
    filters: list[FilterClause]
    rationale: str


class AnalysisResult(BaseModel):
    analysis_type: AnalysisType
    title: str
    summary: dict[str, Any]
    table: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
