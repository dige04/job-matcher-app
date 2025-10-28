"use client";

import React from "react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { Skeleton } from "./ui/skeleton";
import { ArrowLeft, TrendingUp } from "lucide-react";
import axios from "axios";

interface ResultsPageProps {
  onBack: () => void;
  data?: any;
}

export default function ResultsPage({ onBack, data }: ResultsPageProps) {
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<any>(null);

  React.useEffect(() => {
    async function callApi() {
      if (!data) return;
      setLoading(true);
      try {
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/predict`;
        const res = await axios.post(apiUrl, {
          resume_text: data.resume,
          job_title: data.jobTitle,
          job_description: data.jobDescription,
          requirements: data.jobRequirements,
          benefits: data.jobBenefits
        });
        setResult(res.data);
      } catch (err) {
        console.error(err);
        setResult({ error: "Failed to call API" });
      } finally {
        setLoading(false);
      }
    }
    callApi();
  }, [data]);

  if (!data) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card className="p-6">
          <h3>No data provided</h3>
          <Button onClick={onBack}><ArrowLeft className="w-4 h-4 mr-2" />Back</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Analysis result</h2>
          <p className="text-sm text-gray-500">Predicted salary and skills match</p>
        </div>
        <div>
          <Button variant="ghost" onClick={onBack}><ArrowLeft className="w-4 h-4 mr-2"/>Back</Button>
        </div>
      </div>

      <Card className="p-6">
        {loading && <Skeleton className="h-6 w-32 mb-4" />}
        {!loading && result && (
          <div>
            <p><strong>Predicted salary:</strong> {result.predicted_salary ? new Intl.NumberFormat().format(result.predicted_salary) + " VND" : "—"}</p>
            <p><strong>Match score:</strong> {(result.match_score || 0).toFixed(2)}</p>

            <div className="mt-4">
              <h3 className="font-medium">Missing skills</h3>
              {result.missing_skills && result.missing_skills.length ? (
                <ul className="list-disc pl-5">
                  {result.missing_skills.map((s:any, i:number) => <li key={i}>{s}</li>)}
                </ul>
              ) : <p className="text-sm text-gray-500">No major missing skills detected.</p>}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
