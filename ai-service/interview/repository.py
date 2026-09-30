import json
import uuid
from contextlib import contextmanager

from db import get_connection


@contextmanager
def interview_lock(session_id):
    """
    Hold a PostgreSQL advisory transaction lock for one
    interview session.

    Any concurrent request for the same session waits until
    the current request finishes.
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT pg_advisory_xact_lock(
                    hashtextextended(%s, 0)
                )
                """,
                (session_id,),
            )

        yield connection


def get_interview_session(
    session_id,
    connection=None,
):

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    i.id,
                    i."userId",
                    i."jobTitle",
                    i."companyName",
                    i."jobDescription",
                    i."interviewType",
                    i.difficulty,
                    i.status,
                    i."currentTopic",
                    i."topicsCovered",
                    i.strengths,
                    i.weaknesses,
                    i."followUpNeeded",
                    i."interviewPhase",

                    u.name,
                    u.bio,
                    u.experience,
                    u.skills,

                    r.content

                FROM "InterviewSession" i

                JOIN "User" u
                    ON i."userId" = u.id

                LEFT JOIN "Resume" r
                    ON u.id = r."userId"

                WHERE i.id = %s
                """,
                (session_id,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            cursor.execute(
                """
                SELECT
                    id,
                    role,
                    content,
                    score,
                    feedback,
                    "createdAt"
                FROM "InterviewMessage"
                WHERE "sessionId" = %s
                ORDER BY "createdAt" ASC
                """,
                (session_id,),
            )

            message_rows = cursor.fetchall()

            messages = [
                {
                    "id": message[0],
                    "role": message[1],
                    "content": message[2],
                    "score": message[3],
                    "feedback": message[4],
                    "createdAt": message[5],
                }
                for message in message_rows
            ]

            return {
                "id": row[0],
                "userId": row[1],
                "jobTitle": row[2],
                "companyName": row[3],
                "jobDescription": row[4],
                "interviewType": row[5],
                "difficulty": row[6],
                "status": row[7],
                "currentTopic": row[8],
                "topicsCovered": (
                    row[9]
                    if row[9] is not None
                    else []
                ),
                "strengths": (
                    row[10]
                    if row[10] is not None
                    else []
                ),
                "weaknesses": (
                    row[11]
                    if row[11] is not None
                    else []
                ),
                "followUpNeeded": row[12],
                "interviewPhase": row[13],
                "candidateName": row[14],
                "candidateBio": row[15],
                "candidateExperience": row[16],
                "candidateSkills": (
                    row[17]
                    if row[17] is not None
                    else []
                ),
                "resumeContent": row[18],
                "messages": messages,
            }

    finally:

        if owns_connection:
            connection.close()


def update_interview_state(
    session_id,
    current_topic,
    topics_covered,
    strengths,
    weaknesses,
    follow_up_needed,
    interview_phase,
    connection=None,
):

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE "InterviewSession"
                SET
                    "currentTopic" = %s,
                    "topicsCovered" = %s,
                    strengths = %s,
                    weaknesses = %s,
                    "followUpNeeded" = %s,
                    "interviewPhase" = %s
                WHERE id = %s
                """,
                (
                    current_topic,
                    json.dumps(topics_covered),
                    json.dumps(strengths),
                    json.dumps(weaknesses),
                    follow_up_needed,
                    interview_phase,
                    session_id,
                ),
            )

        if owns_connection:
            connection.commit()

    finally:

        if owns_connection:
            connection.close()


def create_interview_message(
    session_id,
    role,
    content,
    connection=None,
):

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO "InterviewMessage"
                    (
                        "id",
                        "sessionId",
                        "role",
                        "content"
                    )
                VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                RETURNING
                    "id",
                    "sessionId",
                    "role",
                    "content",
                    "createdAt"
                """,
                (
                    str(uuid.uuid4()),
                    session_id,
                    role,
                    content,
                ),
            )

            row = cursor.fetchone()

        if owns_connection:
            connection.commit()

        return {
            "id": row[0],
            "sessionId": row[1],
            "role": row[2],
            "content": row[3],
            "createdAt": row[4],
        }

    finally:

        if owns_connection:
            connection.close()


def complete_interview_session(
    session_id,
    connection=None,
):

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE "InterviewSession"
                SET
                    status = 'COMPLETED',
                    "completedAt" = NOW()
                WHERE id = %s
                """,
                (session_id,),
            )

        if owns_connection:
            connection.commit()

    finally:

        if owns_connection:
            connection.close()
            
            