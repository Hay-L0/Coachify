from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auth import verify_ai_service_key

from interview.state import InterviewState
from interview.engine import InterviewEngine
from interview.repository import (
    interview_lock,
    get_interview_session,
    create_interview_message,
    update_interview_state,
    complete_interview_session,
)
from interview.llm import (
    GeminiProvider,
    LLMProviderError,
)

from rag.ingestion import KnowledgeIngestionService


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InterviewRequest(BaseModel):
    sessionId: str
    answer: str


@app.get("/")
def root():
    return {
        "message": "Coachify AI service is running"
    }


@app.post("/interview/start")
def start_interview(
    request: InterviewRequest,
    authenticated: bool = Depends(
        verify_ai_service_key
    ),
):

    with interview_lock(
        request.sessionId
    ) as connection:

        session = get_interview_session(
            request.sessionId,
            connection=connection,
        )

        if not session:
            return {
                "error": "Interview session not found"
            }

        if session["status"] != "IN_PROGRESS":
            return {
                "error": "Interview is not active"
            }

        if len(session["messages"]) > 0:

            first_message = next(
                (
                    message
                    for message in session["messages"]
                    if message["role"] == "assistant"
                ),
                None,
            )

            if first_message:
                return {
                    "response": first_message["content"],
                    "alreadyStarted": True,
                }

            return {
                "error": "Interview has already started"
            }

        ingestion = KnowledgeIngestionService()

        ingestion.ingest_session_context(
            session_id=request.sessionId,
            user_id=session["userId"],
            resume_content=session["resumeContent"],
            job_description=session["jobDescription"],
        )

        state = InterviewState(
            session_id=request.sessionId,
            job_title=session["jobTitle"],
            company_name=session["companyName"],
            job_description=session["jobDescription"],
            interview_type=session["interviewType"],
            difficulty=session["difficulty"],
            candidate_name=session["candidateName"],
            candidate_bio=session["candidateBio"],
            candidate_experience=session[
                "candidateExperience"
            ],
            candidate_skills=session["candidateSkills"],
            resume_content=session["resumeContent"],
            messages=[],
            current_topic=session["currentTopic"],
            topics_covered=session["topicsCovered"],
            strengths=session["strengths"],
            weaknesses=session["weaknesses"],
            follow_up_needed=session[
                "followUpNeeded"
            ],
            interview_phase=session[
                "interviewPhase"
            ],
        )

        llm = GeminiProvider()

        result = llm.generate_response(
            state
        )

        response = result["response"]

        state.current_topic = result.get(
            "currentTopic",
            state.current_topic,
        )

        state.topics_covered = (
            result.get(
                "topicsCovered",
                state.topics_covered,
            )
            or state.topics_covered
        )

        state.strengths = (
            result.get(
                "strengths",
                state.strengths,
            )
            or state.strengths
        )

        state.weaknesses = (
            result.get(
                "weaknesses",
                state.weaknesses,
            )
            or state.weaknesses
        )

        state.follow_up_needed = result.get(
            "followUpNeeded",
            state.follow_up_needed,
        )

        create_interview_message(
            request.sessionId,
            "assistant",
            response,
            connection=connection,
        )

        update_interview_state(
            request.sessionId,
            state.current_topic,
            state.topics_covered,
            state.strengths,
            state.weaknesses,
            state.follow_up_needed,
            state.interview_phase,
            connection=connection,
        )

        connection.commit()

        return {
            "response": response,
            "action": result.get(
                "action",
                "NEXT_TOPIC",
            ),
            "alreadyStarted": False,
        }


@app.post("/interview")
def interview(
    request: InterviewRequest,
    authenticated: bool = Depends(
        verify_ai_service_key
    ),
):

    if not request.answer.strip():
        return {
            "error": "Interview answer cannot be empty"
        }

    with interview_lock(
        request.sessionId
    ) as connection:

        session = get_interview_session(
            request.sessionId,
            connection=connection,
        )

        if not session:
            return {
                "error": "Interview session not found"
            }

        if session["status"] != "IN_PROGRESS":
            return {
                "error": "Interview is not active"
            }

        state = InterviewState(
            session_id=request.sessionId,
            job_title=session["jobTitle"],
            company_name=session["companyName"],
            job_description=session["jobDescription"],
            interview_type=session["interviewType"],
            difficulty=session["difficulty"],
            candidate_name=session["candidateName"],
            candidate_bio=session["candidateBio"],
            candidate_experience=session[
                "candidateExperience"
            ],
            candidate_skills=session["candidateSkills"],
            resume_content=session["resumeContent"],
            messages=session["messages"],
            current_topic=session["currentTopic"],
            topics_covered=session["topicsCovered"],
            strengths=session["strengths"],
            weaknesses=session["weaknesses"],
            follow_up_needed=session[
                "followUpNeeded"
            ],
            interview_phase=session[
                "interviewPhase"
            ],
        )

        engine = InterviewEngine(
            state,
            GeminiProvider(),
        )

        try:

            result = engine.process_answer(
                request.answer
            )

        except LLMProviderError as error:

            if error.error_type == "quota_exceeded":

                return {
                    "error": (
                        "Jabari is temporarily unavailable "
                        "because the current AI provider has "
                        "reached its usage quota."
                    ),
                    "provider": error.provider,
                    "errorType": error.error_type,
                    "retryable": error.retryable,
                }

            raise

        response = result["response"]

        create_interview_message(
            request.sessionId,
            "user",
            request.answer,
            connection=connection,
        )

        update_interview_state(
            request.sessionId,
            state.current_topic,
            state.topics_covered,
            state.strengths,
            state.weaknesses,
            state.follow_up_needed,
            state.interview_phase,
            connection=connection,
        )

        create_interview_message(
            request.sessionId,
            "assistant",
            response,
            connection=connection,
        )

        if result["action"] == "COMPLETE":

            complete_interview_session(
                request.sessionId,
                connection=connection,
            )

        connection.commit()

        return {
            "response": response,
            "action": result["action"],
            "questionsAsked": state.questions_asked,
            "topicsCovered": state.topics_covered,
            "currentTopic": state.current_topic,
            "interviewPhase": state.interview_phase,
            "followUpNeeded": state.follow_up_needed,
        }