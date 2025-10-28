"use client";

import { Button } from "./ui/button";

interface HeaderProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export default function Header({ currentPage, onNavigate }: HeaderProps) {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white">P</span>
            </div>
            <h1 className="text-gray-900 cursor-pointer" onClick={() => onNavigate('home')}>
              <span className="hidden sm:inline">PhoBERT Job Matcher</span>
              <span className="sm:hidden">PhoBERT</span>
            </h1>
          </div>
          
          <nav className="flex items-center gap-1">
            <Button variant="ghost" onClick={() => onNavigate('home')} className="text-sm">Home</Button>
            <Button variant="ghost" onClick={() => onNavigate('results')} className="text-sm">Results</Button>
            <Button variant="ghost" onClick={() => onNavigate('about')} className="text-sm">About</Button>
            <Button
              variant="ghost"
              onClick={() => window.open('https://huggingface.co/docs', '_blank')}
              className="text-sm"
            >
              Docs
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
}
