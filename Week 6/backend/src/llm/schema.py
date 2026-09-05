from enum import Enum
from pydantic import BaseModel, Field

# 1. Closed Enums
class CategoryEnum(str, Enum):
    BILLING = "billing"
    BUG = "bug"
    FEATURE = "feature"
    OTHER = "other"

class UrgencyEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

# 2. Input Schema
class TriageRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The customer support message text (1-2000 characters)."
    )

# 3. Output Schema
class TriageResponse(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    reason: str = Field(..., min_length=1, description="One concise sentence explaining the classification")