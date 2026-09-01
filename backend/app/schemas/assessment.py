# assessment.py
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AssessmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    topic: str = Field(..., min_length=1, max_length=200)
    total_questions: int = Field(default=5, ge=1, le=100)
    difficulty: str = "medium"


class AssessmentCreate(AssessmentBase):
    lesson_id: Optional[int] = None
    student_id: Optional[int] = None


class AssessmentQuestion(BaseModel):
    question: str
    options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = Field(default=1, ge=1)


class AssessmentAnswer(BaseModel):
    question_id: Optional[int] = None
    answer: str


class AssessmentSubmit(BaseModel):
    assessment_id: int
    answers: List[AssessmentAnswer] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    assessment_id: int
    score: float = Field(default=0, ge=0)
    total_points: int = Field(default=0, ge=0)
    percentage: float = Field(default=0, ge=0, le=100)
    correct_answers: int = Field(default=0, ge=0)
    total_questions: int = Field(default=0, ge=0)
    feedback: Optional[str] = None
    details: List[Dict[str, Any]] = Field(default_factory=list)


class AssessmentResponse(AssessmentBase):
    id: int
    lesson_id: Optional[int] = None
    student_id: Optional[int] = None
    questions: List[AssessmentQuestion] = Field(default_factory=list)
    status: str = "created"

    model_config = {
        "from_attributes": True
    }