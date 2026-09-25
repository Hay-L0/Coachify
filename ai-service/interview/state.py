class InterviewState:

    def __init__(
        self,
        session_id,
        job_title,
        interview_type,
        difficulty,
        messages=None,
        current_topic=None,
        topics_covered=None,
        strengths=None,
        weaknesses=None,
        follow_up_needed=False,
        interview_phase=None,
        candidate_name=None,
        candidate_bio=None,
        candidate_experience=None,
        candidate_skills=None,
        resume_content=None,
        company_name=None,
        job_description=None,
    ):

        self.session_id = session_id

        self.job_title = job_title
        self.company_name = company_name
        self.job_description = job_description

        self.interview_type = interview_type
        self.difficulty = difficulty

        self.candidate_name = candidate_name
        self.candidate_bio = candidate_bio
        self.candidate_experience = candidate_experience

        self.candidate_skills = (
            candidate_skills
            if candidate_skills is not None
            else []
        )

        self.resume_content = resume_content

        self.messages = (
            messages
            if messages is not None
            else []
        )

        self.questions_asked = sum(
            1
            for message in self.messages
            if message["role"] == "user"
        )

        self.current_topic = current_topic

        self.topics_covered = (
            topics_covered
            if topics_covered is not None
            else []
        )

        self.strengths = (
            strengths
            if strengths is not None
            else []
        )

        self.weaknesses = (
            weaknesses
            if weaknesses is not None
            else []
        )

        self.follow_up_needed = follow_up_needed

        self.interview_phase = (
            interview_phase
            if interview_phase is not None
            else self._determine_phase()
        )

    def _determine_phase(self):

        if self.questions_asked == 0:
            return "INTRODUCTION"

        if self.questions_asked <= 2:
            return "WARM_UP"

        return "INTERVIEW"