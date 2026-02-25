"""
Normalization Result Model

Schema for normalization operation result
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from .normalized_parameter import NormalizedParameter


class NormalizationResult(BaseModel):
    """Schema for normalization result"""
    success: bool = Field(..., description="Whether normalization succeeded")
    normalized_parameter: Optional[NormalizedParameter] = Field(None, description="Normalized parameter data if successful")
    operations_logged: int = Field(0, description="Number of operations logged to audit trail")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")
    flagged_for_review: bool = Field(False, description="Whether this normalization requires human review")
