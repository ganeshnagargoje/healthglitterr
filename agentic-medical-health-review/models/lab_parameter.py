"""
Lab Parameter Model

Schema for input lab parameter data
"""

from pydantic import BaseModel, Field
from typing import Optional


class LabParameter(BaseModel):
    """Schema for input lab parameter"""
    parameter_id: str = Field(..., description="UUID of the health parameter")
    user_id: str = Field(..., description="User ID")
    parameter_name: str = Field(..., description="Original parameter name from lab report")
    value: float = Field(..., description="Measured value")
    unit: Optional[str] = Field(None, description="Original unit")
    reference_range: Optional[str] = Field(None, description="Original reference range string")
