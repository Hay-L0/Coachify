"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { startInterview, submitAnswer } from "@/actions/interview";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export default function InterviewSessionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  const handleStart = async () => {
    try {
      setLoading(true);
      const newSession = await startInterview({ category: "Technical" });
      setSession(newSession);
      toast.success("Interview started");
    } catch (error) {
      toast.error(error.message || "Failed to start interview");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      toast.error("Please type an answer");
      return;
    }

    try {
      setLoading(true);
      const result = await submitAnswer({
        messages: session.messages,
        answer: answer.trim(),
      });

      setSession({
        ...session,
        messages: result.messages,
      });
      setAnswer("");

      if (result.isComplete) {
        setIsComplete(true);
        toast.success("Interview completed!");
      }
    } catch (error) {
      toast.error(error.message || "Failed to submit answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Interview Session</h1>
        <p className="text-muted-foreground mt-1">
          Answer the questions as you would in a real interview.
        </p>
      </div>

      {!session ? (
        <Card>
          <CardHeader>
            <CardTitle>Start Interview</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={handleStart} disabled={loading} size="lg">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                "Start Interview"
              )}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Conversation */}
          <Card>
            <CardHeader>
              <CardTitle>Conversation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 max-h-[400px] overflow-y-auto">
              {session.messages.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    msg.role === "assistant"
                      ? "bg-muted"
                      : "bg-primary/10 ml-8"
                  }`}
                >
                  <p className="text-sm font-medium mb-1">
                    {msg.role === "assistant" ? "Interviewer" : "You"}
                  </p>
                  <p>{msg.content}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Answer Box */}
          {!isComplete ? (
            <Card>
              <CardContent className="pt-6 space-y-4">
                <Textarea
                  placeholder="Type your answer here..."
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  rows={4}
                />
                <Button
                  onClick={handleSubmitAnswer}
                  disabled={loading || !answer.trim()}
                >
                  {loading ? (
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
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <h3 className="text-xl font-semibold mb-2">Interview Complete</h3>
                <p className="text-muted-foreground mb-4">
                  Next we will add scoring and feedback.
                </p>
                <Button onClick={() => router.push("/interview")}>
                  Back to Interviews
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}