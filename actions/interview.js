"use server";

import { db } from "@/lib/prisma";
import { auth } from "@clerk/nextjs/server";
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-3.6-flash" });

// ============================================
// Get past assessments
// ============================================
export async function getAssessments() {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthorized");

  const user = await db.user.findUnique({
    where: { ClerkUserId: userId },
  });

  if (!user) throw new Error("User not found");

  return await db.assessment.findMany({
    where: { userId: user.id },
    orderBy: { createAt: "asc" },
  });
}

// ============================================
// Start Interview
// ============================================
export async function startInterview({ category = "Technical" } = {}) {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthorized");

  const user = await db.user.findUnique({
    where: { ClerkUserId: userId },
    select: {
      industry: true,
      skills: true,
      experience: true,
      bio: true,
    },
  });

  if (!user) throw new Error("User not found");

  // Generate the first question
  const prompt = `
You are a professional technical interviewer.
The candidate works in: ${user.industry || "General"}
Skills: ${user.skills?.join(", ") || "Not specified"}
Experience: ${user.experience || 0} years

Ask the FIRST interview question only.
Make it relevant and open-ended.
Do not include any explanation, just the question.
`;

  const result = await model.generateContent(prompt);
  const firstQuestion = result.response.text().trim();

  return {
    sessionId: crypto.randomUUID(),
    category,
    startedAt: new Date().toISOString(),
    messages: [
      {
        role: "assistant",
        content: firstQuestion,
      },
    ],
  };
}

// ============================================
// Submit Answer + Get Next Question
// ============================================
export async function submitAnswer({ messages, answer }) {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthorized");

  const user = await db.user.findUnique({
    where: { ClerkUserId: userId },
    select: {
      industry: true,
      skills: true,
    },
  });

  if (!user) throw new Error("User not found");

  // Add the user's answer to the conversation
  const updatedMessages = [
    ...messages,
    { role: "user", content: answer },
  ];

  // Ask the AI for the next question or to end
  const conversationText = updatedMessages
    .map((m) => `${m.role === "assistant" ? "Interviewer" : "Candidate"}: ${m.content}`)
    .join("\n");

  const prompt = `
You are a professional technical interviewer.
Industry: ${user.industry || "General"}
Skills: ${user.skills?.join(", ") || "Not specified"}

Here is the conversation so far:
${conversationText}

Based on the candidate's last answer, either:
1. Ask a good follow-up question, OR
2. If you have asked enough (around 5-7 questions), say exactly: "INTERVIEW_COMPLETE"

Only reply with the next question or the exact words INTERVIEW_COMPLETE.
`;

  const result = await model.generateContent(prompt);
  const aiResponse = result.response.text().trim();

  if (aiResponse === "INTERVIEW_COMPLETE") {
    return {
      messages: updatedMessages,
      isComplete: true,
    };
  }

  // Add AI's next question
  updatedMessages.push({
    role: "assistant",
    content: aiResponse,
  });

  return {
    messages: updatedMessages,
    isComplete: false,
  };
}

