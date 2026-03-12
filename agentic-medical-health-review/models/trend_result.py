"""
Trend Result Model

Schema for trend computation output
"""

from pydantic import BaseModel, Field
from typing import Optional


class TrendResult(BaseModel):
    """Schema for trend computation result"""
    trend_type: str = Field(..., description="Type: increasing, decreasing, stable, insufficient_data")
    confidence_score: float = Field(..., description="Confidence in trend detection (0-1)")
    data_point_count: int = Field(..., description="Number of data points analyzed")
    value_change: Optional[float] = Field(None, description="Absolute change from first to last value")
    percentage_change: Optional[float] = Field(None, description="Percentage change from first to last value")
    average_value: Optional[float] = Field(None, description="Mean value across all data points")
    canonical_name: str = Field(..., description="Parameter name")
    user_id: str = Field(..., description="User ID")
    time_span_days: Optional[float] = Field(None, description="Days between first and last measurement")
