from .state import InterviewState
from .llm import LLMProvider
from rag.retriever import (
    KnowledgeRetriever,
    format_retrieved_context,
)


class InterviewEngine:

    def __init__(
        self,
        state: InterviewState,
        llm: LLMProvider,
        retriever=None,
    ):

        self.state = state
        self.llm = llm

        self.retriever = (
            retriever
            or KnowledgeRetriever()
        )

    def _build_retrieval_query(self, answer):

        recent_messages = self.state.messages[-6:]

        conversation_context = "\n".join(
            [
                f'{message["role"].upper()}: '
                f'{message["content"]}'
                for message in recent_messages
            ]
        )

        return f"""
Target role:
{self.state.job_title}

Interview type:
{self.state.interview_type}

Current interview topic:
{self.state.current_topic or "Not yet established"}

Topics already covered:
{", ".join(self.state.topics_covered) or "None"}

Recent conversation:
{conversation_context}

Candidate's latest answer:
{answer}

Retrieve knowledge that is relevant to understanding
the candidate's latest answer and continuing the interview.

Prioritize information about:

- relevant candidate experience
- projects
- technologies
- responsibilities
- skills
- job requirements
- experience gaps that are relevant to the current topic
""".strip()

    def process_answer(self, answer):

        answer = answer.strip()

        if not answer:
            raise ValueError(
                "Interview answer cannot be empty"
            )

        self.state.messages.append({
            "role": "user",
            "content": answer,
        })

        self.state.questions_asked += 1

        self.state.interview_phase = (
            self.state._determine_phase()
        )

        retrieval_query = (
            self._build_retrieval_query(
                answer
            )
        )

        retrieved_results = (
            self.retriever.retrieve(
                session_id=self.state.session_id,
                query=retrieval_query,
                limit=5,
            )
        )

        retrieved_context = (
            format_retrieved_context(
                retrieved_results
            )
        )

        result = self.llm.generate_response(
            self.state,
            retrieved_context=retrieved_context,
        )

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