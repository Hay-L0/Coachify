from .state import InterviewState
from .llm import LLMProvider


class InterviewEngine:

    def __init__(
        self,
        state: InterviewState,
        llm: LLMProvider,
    ):

        self.state = state
        self.llm = llm

    def process_answer(self, answer):

        # Store the candidate's answer in memory.
        self.state.messages.append({
            "role": "user",
            "content": answer,
        })

        # A question is considered answered when the
        # candidate sends a response.
        self.state.questions_asked += 1

        # Update the broad interview phase.
        self.state.interview_phase = (
            self.state._determine_phase()
        )

        # Ask Jabari what should happen next.
        result = self.llm.generate_response(
            self.state
        )

        # Apply Jabari's structured decision.
        action = result.get(
            "action",
            "NEXT_TOPIC",
        )

        self.state.current_topic = result.get(
            "currentTopic",
            self.state.current_topic,
        )

        self.state.topics_covered = result.get(
            "topicsCovered",
            self.state.topics_covered,
        )

        self.state.strengths = result.get(
            "strengths",
            self.state.strengths,
        )

        self.state.weaknesses = result.get(
            "weaknesses",
            self.state.weaknesses,
        )

        self.state.follow_up_needed = result.get(
            "followUpNeeded",
            False,
        )

        response = result.get(
            "response",
            "",
        )

        # Store Jabari's response in the in-memory
        # conversation.
        self.state.messages.append({
            "role": "assistant",
            "content": response,
        })

        return {
            "action": action,
            "response": response,
            "currentTopic": self.state.current_topic,
            "topicsCovered": self.state.topics_covered,
            "strengths": self.state.strengths,
            "weaknesses": self.state.weaknesses,
            "followUpNeeded": self.state.follow_up_needed,
        }