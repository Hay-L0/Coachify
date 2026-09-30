from interview.state import InterviewState
from interview.engine import InterviewEngine
from interview.llm import GeminiProvider

state = InterviewState(
    session_id="rag-test",
    job_title="Frontend Engineer",
    interview_type="TECHNICAL",
    difficulty="MEDIUM",
    messages=[
        {
            "role": "assistant",
            "content": "Tell me about a recent project you worked on.",
        }
    ],
)

engine = InterviewEngine(
    state,
    GeminiProvider(),
)

result = engine.process_answer(
    "I built a React dashboard using Redux for state management."
)

print("Response:", result["response"])
print("Current topic:", result["currentTopic"])
print("Topics covered:", result["topicsCovered"])
print("Strengths:", result["strengths"])
print("Weaknesses:", result["weaknesses"])
