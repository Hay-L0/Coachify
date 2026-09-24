import json
import uuid

from db import get_connection


def get_interview_session(session_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    i.id,
                    i."userId",
                    i."jobTitle",
                    i."companyName",
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
                "interviewType": row[4],
                "difficulty": row[5],
                "status": row[6],

                "currentTopic": row[7],

                "topicsCovered": (
                    row[8]
                    if row[8] is not None
                    else []
                ),

                "strengths": (
                    row[9]
                    if row[9] is not None
                    else []
                ),

                "weaknesses": (
                    row[10]
                    if row[10] is not None
                    else []
                ),

                "followUpNeeded": row[11],

                "interviewPhase": row[12],

                "candidateName": row[13],
                "candidateBio": row[14],
                "candidateExperience": row[15],
                "candidateSkills": (
                    row[16]
                    if row[16] is not None
                    else []
                ),
                "resumeContent": row[17],

                "messages": messages,
            }


def update_interview_state(
    session_id,
    current_topic,
    topics_covered,
    strengths,
    weaknesses,
    follow_up_needed,
    interview_phase,
):

    with get_connection() as connection:

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

        connection.commit()


def create_interview_message(
    session_id,
    role,
    content,
):

    with get_connection() as connection:

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
                    (%s, %s, %s, %s)
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

        connection.commit()

        return {
            "id": row[0],
            "sessionId": row[1],
            "role": row[2],
            "content": row[3],
            "createdAt": row[4],
        }


def complete_interview_session(session_id):

    with get_connection() as connection:

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

        connection.commit()
            
            