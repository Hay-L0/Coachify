from fastapi import FastAPI
from pydantic import BaseModel

from interview.state import InterviewState
from interview.engine import InterviewEngine

app = FastAPI()


class InterviewRequest(BaseModel):
    jobTitle: str
    interviewType: str
    difficulty: str
    answer: str


@app.get("/")
def root():
    return {"message": "Coachify AI service is running"}


@app.post("/interview")
def interview(request: InterviewRequest):

    state = InterviewState(
        job_title=request.jobTitle,
        interview_type=request.interviewType,
        difficulty=request.difficulty,
    )

    engine = InterviewEngine(state)

    response = engine.process_answer(request.answer)

    return {
        "response": response,
        "questionsAsked": state.questions_asked,
        "topicsCovered": state.topics_covered,
    }