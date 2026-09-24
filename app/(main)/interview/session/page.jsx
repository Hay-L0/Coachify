"use client";

import { useEffect, useRef, useState } from "react";

import { useSearchParams, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Textarea } from "@/components/ui/textarea";

import { Loader2 } from "lucide-react";

import { toast } from "sonner";

export default function InterviewSessionPage() {
  const searchParams = useSearchParams();

  const hasStartedRef = useRef(false);

  const router = useRouter();

  const sessionId = searchParams.get("id");

  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      router.push("/interview");
      return;
    }

    const loadSession = async () => {
      try {
        const response = await fetch(
          `/api/interview/session?id=${sessionId}`
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.error || "Failed to load interview"
          );
        }

        // If this is a brand-new interview,
        // ask the Python AI service for the first question.
        if (data.messages?.length === 0) {
          // Prevent React Strict Mode from starting
          // the same interview twice during development.
          if (hasStartedRef.current) {
            return;
          }

          hasStartedRef.current = true;

          const startResponse = await fetch(
            "http://127.0.0.1:8000/interview/start",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                sessionId,
                answer: "",
              }),
            }
          );

          const startData = await startResponse.json();

          if (!startResponse.ok) {
            throw new Error(
              startData.error ||
                "Failed to start AI interview"
            );
          }

          // Reload the session so the new
          // interviewer message appears.
          const updatedResponse = await fetch(
            `/api/interview/session?id=${sessionId}`
          );

          const updatedData =
            await updatedResponse.json();

          if (!updatedResponse.ok) {
            throw new Error(
              updatedData.error ||
                "Failed to reload interview"
            );
          }

          setSession(updatedData);
        } else {
          setSession(data);
        }
      } catch (error) {
        console.error(error);

        toast.error(
          error.message ||
            "Failed to load interview"
        );

        router.push("/interview");
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, [sessionId, router]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      toast.error("Please type an answer");
      return;
    }

    try {
      setSubmitting(true);

      const response = await fetch(
        "http://127.0.0.1:8000/interview",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            sessionId,
            answer,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            "Failed to submit answer"
        );
      }

      const sessionResponse = await fetch(
        `/api/interview/session?id=${sessionId}`
      );

      const sessionData =
        await sessionResponse.json();

      if (!sessionResponse.ok) {
        throw new Error(
          sessionData.error ||
            "Failed to reload interview"
        );
      }

      setSession(sessionData);
      setAnswer("");
    } catch (error) {
      console.error(error);

      toast.error(
        error.message ||
          "Failed to submit answer"
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">
          {session.jobTitle} Interview
        </h1>

        <p className="text-muted-foreground mt-1">
          {session.interviewType} • {session.difficulty}

          {session.companyName &&
            ` • ${session.companyName}`}
        </p>
      </div>

      {/* Conversation */}
      <Card>
        <CardHeader>
          <CardTitle>
            Interview Conversation
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-4 max-h-[500px] overflow-y-auto">
          {session.messages?.length === 0 ? (
            <p className="text-muted-foreground">
              Your interviewer will ask the first question shortly.
            </p>
          ) : (
            session.messages.map((message) => (
              <div
                key={message.id}
                className={`p-4 rounded-lg ${
                  message.role === "assistant"
                    ? "bg-muted"
                    : "bg-primary/10 ml-8"
                }`}
              >
                <p className="text-sm font-medium mb-1">
                  {message.role === "assistant"
                    ? "Interviewer"
                    : "You"}
                </p>

                <p>{message.content}</p>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Answer */}
      {session.status === "IN_PROGRESS" && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <Textarea
              placeholder="Type your answer here..."
              value={answer}
              onChange={(event) =>
                setAnswer(event.target.value)
              }
              rows={5}
              disabled={submitting}
            />

            <Button
              onClick={handleSubmitAnswer}
              disabled={
                submitting || !answer.trim()
              }
            >
              {submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Thinking...
                </>
              ) : (
                "Submit Answer"
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Completed */}
      {session.status === "COMPLETED" && (
        <Card>
          <CardContent className="py-8 text-center">
            <h3 className="text-xl font-semibold mb-2">
              Interview Complete
            </h3>

            <p className="text-muted-foreground mb-4">
              Your interview has been completed.
            </p>

            <Button
              onClick={() =>
                router.push("/interview")
              }
            >
              Back to Interviews
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
