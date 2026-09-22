from .state import InterviewState


class InterviewEngine:
    def __init__(self, state: InterviewState):
        self.state = state

    def process_answer(self, answer):
        self.state.messages.append({
            "role": "user",
            "content": answer,
        })

        self.state.questions_asked += 1

        return (
            "Thanks for your answer. "
            "Can you tell me more about the specific challenge "
            "you faced and how you solved it?"
        )