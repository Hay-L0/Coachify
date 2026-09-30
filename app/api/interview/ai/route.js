import { NextResponse } from "next/server";
import { checkUser } from "@/lib/checkUser";

export async function POST(request) {
  try {
    const user = await checkUser();

    if (!user) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const body = await request.json();

    const aiServiceUrl =
      process.env.AI_SERVICE_URL ||
      "http://127.0.0.1:8000";

    const aiServiceKey =
      process.env.AI_SERVICE_API_KEY;

    if (!aiServiceKey) {
      console.error(
        "AI_SERVICE_API_KEY is not configured"
      );

      return NextResponse.json(
        {
          error:
            "AI service authentication is not configured",
        },
        { status: 500 }
      );
    }

    const response = await fetch(
      `${aiServiceUrl}/interview`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-AI-Service-Key": aiServiceKey,
        },
        body: JSON.stringify(body),
      }
    );

    const data = await response.json();

    return NextResponse.json(
      data,
      { status: response.status }
    );
  } catch (error) {
    console.error(
      "AI INTERVIEW PROXY ERROR:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Failed to communicate with AI service",
      },
      { status: 500 }
    );
  }
}