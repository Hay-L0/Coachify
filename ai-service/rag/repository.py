import uuid

from db import get_connection


def create_knowledge_chunk(
    session_id,
    user_id,
    source,
    content,
    embedding,
):
    knowledge_id = str(uuid.uuid4())

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO "InterviewKnowledge"
                    (
                        "id",
                        "sessionId",
                        "userId",
                        "source",
                        "content",
                        "embedding"
                    )
                VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::vector
                    )
                RETURNING
                    "id",
                    "sessionId",
                    "userId",
                    "source",
                    "content",
                    "createdAt"
                """,
                (
                    knowledge_id,
                    session_id,
                    user_id,
                    source,
                    content,
                    embedding,
                ),
            )

            row = cursor.fetchone()

        connection.commit()

    return {
        "id": row[0],
        "sessionId": row[1],
        "userId": row[2],
        "source": row[3],
        "content": row[4],
        "createdAt": row[5],
    }


def delete_session_knowledge(session_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM "InterviewKnowledge"
                WHERE "sessionId" = %s
                """,
                (session_id,),
            )

        connection.commit()


def get_session_knowledge(session_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    "id",
                    "sessionId",
                    "userId",
                    "source",
                    "content",
                    "createdAt"
                FROM "InterviewKnowledge"
                WHERE "sessionId" = %s
                ORDER BY "createdAt" ASC
                """,
                (session_id,),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "sessionId": row[1],
            "userId": row[2],
            "source": row[3],
            "content": row[4],
            "createdAt": row[5],
        }
        for row in rows
    ]


def search_knowledge(
    session_id,
    embedding,
    limit=5,
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    "id",
                    "source",
                    "content",
                    1 - (
                        "embedding" <=> %s::vector
                    ) AS similarity
                FROM "InterviewKnowledge"
                WHERE
                    "sessionId" = %s
                    AND "embedding" IS NOT NULL
                ORDER BY
                    "embedding" <=> %s::vector
                LIMIT %s
                """,
                (
                    embedding,
                    session_id,
                    embedding,
                    limit,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "source": row[1],
            "content": row[2],
            "similarity": float(row[3]),
        }
        for row in rows
    ]