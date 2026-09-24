import { NextResponse } from "next/server";
import { checkUser } from "@/lib/checkUser";
import { db } from "@/lib/prisma";

export async function POST(request) {
  try {
    const user = await checkUser();

    if (!user) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const { sessionId, content } = await request.json();

    if (!sessionId || !content?.trim()) {
      return NextResponse.json(
        { error: "Session ID and answer are required" },
        { status: 400 }
      );
    }

    // Make sure this interview belongs to the logged-in user
    const session = await db.interviewSession.findFirst({
      where: {
        id: sessionId,
        userId: user.id,
      },
      include: {
        messages: {
          orderBy: {
            createdAt: "asc",
          },
        },
      },
    });

    if (!session) {
      return NextResponse.json(
        { error: "Interview session not found" },
        { status: 404 }
      );
    }

    if (session.status !== "IN_PROGRESS") {
      return NextResponse.json(
        { error: "This interview is already completed" },
        { status: 400 }
      );
    }

    // Save the candidate's answer
    await db.interviewMessage.create({
      data: {
        sessionId: session.id,
        role: "user",
        content: content.trim(),
      },
    });

    // Temporary interviewer response.
    // We will replace this with the actual AI later.
    const interviewerQuestion =
      "Thanks for your answer. Can you tell me more about the specific challenge you faced and how you solved it?";

    await db.interviewMessage.create({
      data: {
        sessionId: session.id,
        role: "assistant",
        content: interviewerQuestion,
      },
    });

    // Get the updated conversation
    const updatedSession = await db.interviewSession.findUnique({
      where: {
        id: session.id,
      },
      include: {
        messages: {
          orderBy: {
            createdAt: "asc",
          },
        },
      },
    });

    return NextResponse.json(updatedSession);

  } catch (error) {
    console.error("INTERVIEW MESSAGE ERROR:", error);

    return NextResponse.json(
      { error: "Failed to process interview answer" },
      { status: 500 }
    );
  }
}