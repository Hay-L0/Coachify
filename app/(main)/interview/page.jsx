import { getAssessments } from "@/actions/interview";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function InterviewPage() {
  const assessments = await getAssessments();

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Interviewer</h1>
          <p className="text-muted-foreground mt-1">
            Practice real interviews with an AI that adapts to your answers.
          </p>
        </div>

        <Link href="/interview/session">
          <Button size="lg">Start New Interview</Button>
        </Link>
      </div>

      {/* Past Interviews */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Past Interviews</h2>

        {assessments.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              You haven’t completed any interviews yet.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {assessments.map((assessment) => (
              <Card key={assessment.id}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    {assessment.category} Interview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">
                    {assessment.quizScore?.toFixed(1) || 0}%
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {new Date(assessment.createAt).toLocaleDateString()}
                  </p>
                  {assessment.improvementTip && (
                    <p className="text-sm mt-3 text-muted-foreground">
                      {assessment.improvementTip}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
