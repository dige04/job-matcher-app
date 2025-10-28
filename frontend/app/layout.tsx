// "use client" is not required for layout; pages will opt-in as needed.

import "../styles/globals.css";

export const metadata = {
  title: "PhoBERT Job Matcher",
  description: "Predict salaries and suggest missing skills from resumes vs job postings."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-slate-900">
        {children}
      </body>
    </html>
  );
}
