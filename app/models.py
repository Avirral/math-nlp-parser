from pydantic import BaseModel, Field
from typing import Optional

class MathQuery(BaseModel):
    """Input model for mathematical expression queries"""
    text: str = Field(..., description="Natural language mathematical expression")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "integrate x squared with respect to y"
            }
        }

class MathResponse(BaseModel):
    """Response model containing parsed mathematical expression"""
    latex: str = Field(..., description="LaTeX representation of the expression")
    plain_text: str = Field(..., description="Plain text representation")
    method_used: str = Field(..., description="Method used: 'pattern_matching' or 'nlp'")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latex": "\\int x^2 \\, dy",
                "plain_text": "Integral of x^2 with respect to y",
                "method_used": "pattern_matching",
                "confidence": 0.95
            }
        }
