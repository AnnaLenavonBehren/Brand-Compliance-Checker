from pydantic import BaseModel, field_validator, conlist
from typing import Any

# Model for style guide summarization
class ComplianceInformationModel(BaseModel):
    font_styles : list
    logo_safe_zone : str
    color_palette : list
    company_name : str

# Model to efficiently store results of a compliance check
class ResultModel(BaseModel):
    category: str
    requirement: int
    reason: str

    # Guarantee that the results are actually either 0 or 1 (and integer values), default to 0
    @field_validator('requirement', mode='before')
    @classmethod
    def cast_to_binary(cls, value: Any) -> int:
        v = str(value).strip().lower()
        if v in {"1", "yes", "true"}:
            return 1
        elif v in {"0", "no", "false"}:
            return 0
        else:
            return 0

# Combine four ResultModels so that each compliance check category can be saved individually but within MultiResultModel
class MultiResultModel(BaseModel):
    results: conlist(ResultModel, min_length = 4, max_length = 4)