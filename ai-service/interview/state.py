class InterviewState:
    def __init__(
        self,
        job_title,
        interview_type,
        difficulty,
    ):
        self.job_title = job_title
        self.interview_type = interview_type
        self.difficulty = difficulty

        self.messages = []
        self.topics_covered = []
        self.questions_asked = 0