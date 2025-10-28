"use client";

import { useState } from "react";
import Header from "../components/Header";
import HomePage from "../components/HomePage";
import ResultsPage from "../components/ResultsPage";
import AboutPage from "../components/AboutPage";
import { Toaster } from "../components/ui/sonner";

type Page = "home" | "results" | "about";

export default function Page() {
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const [analysisData, setAnalysisData] = useState<any>(null);

  const handleNavigate = (page: Page) => setCurrentPage(page);

  const handleAnalyze = (data: any) => {
    setAnalysisData(data);
    setCurrentPage("results");
  };

  return (
    <div className="min-h-screen">
      <Header currentPage={currentPage} onNavigate={(p: string) => handleNavigate(p as Page)} />

      <main>
        {currentPage === "home" && <HomePage onAnalyze={handleAnalyze} />}
        {currentPage === "results" && <ResultsPage onBack={() => setCurrentPage("home")} data={analysisData} />}
        {currentPage === "about" && <AboutPage />}
      </main>

      <Toaster />
    </div>
  );
}
