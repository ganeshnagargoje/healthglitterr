"""
Normalized Parameter Model

Schema for normalized parameter output
"""

from pydantic import BaseModel, Field
from typing import Optional


class NormalizedParameter(BaseModel):
    """Schema for normalized parameter output"""
    normalized_parameter_id: str = Field(..., description="UUID of normalized parameter")
    original_parameter_id: str = Field(..., description="UUID of original health parameter")
    user_id: str = Field(..., description="User ID")
    canonical_name: str = Field(..., description="Standardized parameter name")
    original_value: float = Field(..., description="Original measured value")
    original_unit: Optional[str] = Field(None, description="Original unit from lab report")
    normalized_value: float = Field(..., description="Value converted to standard unit")
    standard_unit: str = Field(..., description="Standard unit for this parameter")
    conversion_factor: Optional[float] = Field(None, description="Factor used for unit conversion")
    reference_range_min: Optional[float] = Field(None, description="Minimum reference range value")
    reference_range_max: Optional[float] = Field(None, description="Maximum reference range value")
    normalization_confidence: float = Field(..., description="Confidence score (0-1) for normalization")
