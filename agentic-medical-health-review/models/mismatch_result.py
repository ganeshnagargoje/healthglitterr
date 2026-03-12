"""
Mismatch Result Model

Schema for mismatch detection output
"""

from pydantic import BaseModel, Field
from typing import Optional


class MismatchResult(BaseModel):
    """Schema for mismatch detection result"""
    has_mismatch: bool = Field(..., description="Whether value is outside reference range")
    mismatch_type: str = Field(..., description="Type: above_range, below_range, within_range, no_reference")
    deviation_percentage: Optional[float] = Field(None, description="Percentage deviation from range")
    severity: str = Field(..., description="Severity level: none, mild, moderate, severe")
    normalized_parameter_id: str = Field(..., description="UUID of normalized parameter")
    canonical_name: str = Field(..., description="Canonical parameter name")
    normalized_value: float = Field(..., description="Measured value in standard unit")
    reference_range_min: Optional[float] = Field(None, description="Minimum reference value")
    reference_range_max: Optional[float] = Field(None, description="Maximum reference value")
