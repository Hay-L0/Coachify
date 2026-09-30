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

    def _merge_topics(
        self,
        existing_topics,
        suggested_topics,
        current_topic,
    ):
        """
        Merge topics deterministically.

        The LLM may suggest topics, but Python owns the
        authoritative interview state.
        """

        merged_topics = []

        for topic in [
            *(existing_topics or []),
            *(suggested_topics or []),
        ]:

            if not topic:
                continue

            topic = str(topic).strip()

            if not topic:
                continue

            if topic not in merged_topics:
                merged_topics.append(topic)

        if current_topic:
            current_topic = str(
                current_topic
            ).strip()

            if (
                current_topic
                and current_topic not in merged_topics
            ):
                merged_topics.append(
                    current_topic
                )

        return merged_topics

    def _merge_list(
        self,
        existing_items,
        new_items,
    ):
        """
        Merge LLM-provided state without allowing
        previously recorded information to disappear.
        """

        merged_items = []

        for item in [
            *(existing_items or []),
            *(new_items or []),
        ]:

            if not item:
                continue

            item = str(item).strip()

            if not item:
                continue

            if item not in merged_items:
                merged_items.append(item)

        return merged_items

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

        next_topic = result.get(
            "currentTopic"
        )

        if next_topic:
            self.state.current_topic = (
                str(next_topic).strip()
            )

        self.state.topics_covered = (
            self._merge_topics(
                existing_topics=(
                    self.state.topics_covered
                ),
                suggested_topics=(
                    result.get("topicsCovered")
                ),
                current_topic=(
                    self.state.current_topic
                ),
            )
        )

        self.state.strengths = (
            self._merge_list(
                existing_items=self.state.strengths,
                new_items=result.get("strengths"),
            )
        )

        self.state.weaknesses = (
            self._merge_list(
                existing_items=self.state.weaknesses,
                new_items=result.get("weaknesses"),
            )
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