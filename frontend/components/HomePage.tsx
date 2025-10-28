"use client";

import { useState } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Card } from "./ui/card";
import { Upload, Sparkles } from "lucide-react";

interface HomePageProps {
  onAnalyze: (data: any) => void;
}

export default function HomePage({ onAnalyze }: HomePageProps) {
  const [uploadedResume, setUploadedResume] = useState("");
  const [manualResumeText, setManualResumeText] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [jobRequirements, setJobRequirements] = useState("");
  const [jobBenefits, setJobBenefits] = useState("");
  const [fileName, setFileName] = useState("");

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        setUploadedResume(text);
      };
      reader.readAsText(file);
    }
  };

  const resume = uploadedResume || manualResumeText;

  const isFormValid = !!resume && !!jobDescription;

  const handleAnalyzeClick = () => {
    if (!isFormValid) return;
    onAnalyze({
      resume,
      jobTitle,
      jobDescription,
      jobRequirements,
      jobBenefits
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card className="p-6">
        <h2 className="text-lg font-medium">Resume</h2>
        <p className="text-sm text-gray-500">Paste your resume or upload a .txt file</p>
        <div className="mt-4 space-y-2">
          <input type="file" accept=".txt,.md" onChange={handleFileUpload} />
          <Textarea value={manualResumeText} onChange={(e:any) => setManualResumeText(e.target.value)} placeholder="Or paste resume here..." />
          <p className="text-sm text-gray-500">{fileName}</p>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-medium">Job Posting</h2>
        <div className="mt-4 grid grid-cols-1 gap-4">
          <Input value={jobTitle} onChange={(e:any)=> setJobTitle(e.target.value)} placeholder="Job title" />
          <Textarea value={jobDescription} onChange={(e:any) => setJobDescription(e.target.value)} placeholder="Job description" />
          <Textarea value={jobRequirements} onChange={(e:any) => setJobRequirements(e.target.value)} placeholder="Requirements (bullet points)" />
          <Textarea value={jobBenefits} onChange={(e:any) => setJobBenefits(e.target.value)} placeholder="Benefits" />
        </div>
      </Card>

      <div className="flex items-center justify-end gap-4">
        <Button onClick={handleAnalyzeClick} disabled={!isFormValid}>
          <Sparkles className="w-4 h-4 mr-2" />
          Analyze Match
        </Button>
      </div>
    </div>
  );
}
