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

    const {
      jobTitle,
      companyName,
      jobDescription,
      interviewType,
      difficulty,
    } = await request.json();

    if (!jobTitle || !interviewType || !difficulty) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const interview = await db.interviewSession.create({
      data: {
        userId: user.id,
        jobTitle,
        companyName: companyName || null,
        jobDescription: jobDescription || null,
        interviewType,
        difficulty,
      },
    });

    return NextResponse.json(
      interview,
      { status: 201 }
    );
  } catch (error) {
    console.error(
      "START INTERVIEW ERROR:",
      error
    );

    return NextResponse.json(
      { error: "Failed to start interview" },
      { status: 500 }
    );
  }
}