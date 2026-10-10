from interview.engine import InterviewEngine
from interview.llm import LLMProviderError
from interview.repository import (
    interview_lock,
    get_interview_session,
    create_interview_message,
    update_interview_state,
    complete_interview_session,
)
from interview.state import InterviewState
from interview.provider import ProviderRouter


class VoiceInterviewService:
    """
    Connects the LiveKit voice agent to Coachify's existing
    InterviewEngine.

    The voice agent should not contain interview logic.
    It only passes the candidate's transcript here and
    receives Jabari's next response.
    """

    def process_answer(
        self,
        session_id: str,
        answer: str,
    ):
        if not answer or not answer.strip():
            raise ValueError(
                "Interview answer cannot be empty"
            )

        answer = answer.strip()

        with interview_lock(session_id) as connection:

            session = get_interview_session(
                session_id,
                connection=connection,
            )

            if not session:
                raise ValueError(
                    "Interview session not found"
                )

            if session["status"] != "IN_PROGRESS":
                raise ValueError(
                    "Interview is not active"
                )

            state = InterviewState(
                session_id=session["id"],
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
                candidate_skills=session[
                    "candidateSkills"
                ],
                resume_content=session[
                    "resumeContent"
                ],
                messages=session["messages"],
                current_topic=session["currentTopic"],
                topics_covered=session[
                    "topicsCovered"
                ],
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
                ProviderRouter(),
            )

            try:
                result = engine.process_answer(
                    answer
                )

            except LLMProviderError:
                raise

            response = result["response"]

            create_interview_message(
                session_id,
                "user",
                answer,
                connection=connection,
            )

            update_interview_state(
                session_id,
                state.current_topic,
                state.topics_covered,
                state.strengths,
                state.weaknesses,
                state.follow_up_needed,
                state.interview_phase,
                connection=connection,
            )

            create_interview_message(
                session_id,
                "assistant",
                response,
                connection=connection,
            )

            if result["action"] == "COMPLETE":
                complete_interview_session(
                    session_id,
                    connection=connection,
                )

            connection.commit()

            return {
                "response": response,
                "action": result["action"],
                "questionsAsked": (
                    state.questions_asked
                ),
                "topicsCovered": (
                    state.topics_covered
                ),
                "currentTopic": (
                    state.current_topic
                ),
                "interviewPhase": (
                    state.interview_phase
                ),
                "followUpNeeded": (
                    state.follow_up_needed
                ),
            }