"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function InterviewPage() {
  const router = useRouter();

  const [jobTitle, setJobTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [interviewType, setInterviewType] = useState("TECHNICAL");
  const [difficulty, setDifficulty] = useState("MEDIUM");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const startInterview = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/interview/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jobTitle,
          companyName,
          interviewType,
          difficulty,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to start interview");
      }

      router.push(`/interview/session?id=${data.id}`);
    } catch (error) {
      console.error(error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold">AI Interviewer</h1>

        <p className="text-muted-foreground mt-1">
          Practice real interviews with an AI that adapts to your answers.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Set Up Your Interview</CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Job Title */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              Job Title
            </label>

            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g. Frontend Engineer"
              className="w-full rounded-md border px-3 py-2 outline-none focus:ring-2"
            />
          </div>

          {/* Company */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              Company
              <span className="text-muted-foreground ml-1">
                (optional)
              </span>
            </label>

            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Google"
              className="w-full rounded-md border px-3 py-2 outline-none focus:ring-2"
            />
          </div>

          {/* Interview Type */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              Interview Type
            </label>

            <select
              value={interviewType}
              onChange={(e) => setInterviewType(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
            >
              <option value="TECHNICAL">Technical</option>
              <option value="BEHAVIORAL">Behavioral</option>
              <option value="MIXED">Mixed</option>
            </select>
          </div>

          {/* Difficulty */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              Difficulty
            </label>

            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
            >
              <option value="EASY">Easy</option>
              <option value="MEDIUM">Medium</option>
              <option value="HARD">Hard</option>
            </select>
          </div>

          {error && (
            <p className="text-sm text-red-500">
              {error}
            </p>
          )}

          <Button
            size="lg"
            className="w-full"
            onClick={startInterview}
            disabled={loading || !jobTitle}
          >
            {loading ? "Starting Interview..." : "Start Interview"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
