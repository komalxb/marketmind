"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

function splitReportIntoSections(markdown) {
  if (!markdown) return [];
  const lines = markdown.split("\n");
  const sections = [];
  let current = null;
  for (const line of lines) {
    const match = line.match(/^##\s+(.+)$/);
    if (match) {
      if (current) sections.push(current);
      current = { title: match[1].trim(), body: "" };
    } else {
      if (!current) current = { title: "Overview", body: "" };
      current.body += line + "\n";
    }
  }
  if (current) sections.push(current);
  return sections
    .map((s) => ({ ...s, body: s.body.trim() }))
    .filter((s) => s.body.length > 0);
}

const reportMarkdownComponents = {
  p: ({ children }) => {
    const arr = Array.isArray(children) ? children : [children];
    const first = arr[0];
    const second = arr[1];
    const isLabelParagraph =
      first &&
      typeof first === "object" &&
      first.type === "strong" &&
      typeof second === "string" &&
      second.trimStart().startsWith(":");

    if (isLabelParagraph) {
      const label = first.props.children;
      const restText = second.replace(/^\s*:\s*/, "");
      const tail = arr.slice(2);
      return (
        <div className="mb-4 last:mb-0">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 mb-1.5">
            {label}
          </div>
          <p className="text-sm text-gray-300 leading-relaxed">
            {restText}
            {tail}
          </p>
        </div>
      );
    }
    return (
      <p className="text-sm text-gray-300 leading-relaxed mb-3 last:mb-0">
        {children}
      </p>
    );
  },
  ul: ({ children }) => (
    <ul className="list-disc pl-5 space-y-1.5 text-sm text-gray-300 mb-3 last:mb-0 marker:text-gray-600">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal pl-5 space-y-1.5 text-sm text-gray-300 mb-3 last:mb-0 marker:text-gray-600">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  h3: ({ children }) => (
    <h3 className="text-sm font-semibold text-gray-100 mt-4 mb-2 first:mt-0">
      {children}
    </h3>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-400 hover:text-blue-300 underline underline-offset-2"
    >
      {children}
    </a>
  ),
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showPlan, setShowPlan] = useState(true);

  const handleResearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });

      if (!response.ok) throw new Error("Research failed");
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Something went wrong. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !loading) handleResearch();
  };

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-8 text-center">
        <h1 className="text-4xl font-semibold tracking-tight">MarketMind</h1>
        <p className="text-base text-gray-400 mt-2">
          Research smarter, faster
        </p>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Query Input */}
        <div className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What is driving oil prices right now?"
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm placeholder-gray-500 focus:outline-none focus:border-gray-500 transition-colors"
          />
          <button
            onClick={handleResearch}
            disabled={loading || !query.trim()}
            className="bg-white text-gray-950 px-5 py-3 rounded-lg text-sm font-medium hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Researching..." : "Research →"}
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="mt-10 space-y-3">
            {["Planning research strategy...", "Searching the web...", "Evaluating coverage...", "Synthesizing report..."].map((step, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-gray-400">
                <div className="w-1.5 h-1.5 rounded-full bg-gray-500 animate-pulse" />
                {step}
              </div>
            ))}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 p-4 bg-red-950 border border-red-800 rounded-lg text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="mt-8 space-y-6">
            
            {/* Research Plan */}
            <div className="border border-gray-800 rounded-lg overflow-hidden">
              <button
                onClick={() => setShowPlan(!showPlan)}
                className="w-full flex items-center justify-between px-4 py-3 bg-gray-900 text-sm font-medium hover:bg-gray-800 transition-colors"
              >
                <span>Research Plan · {result.sub_questions.length} questions · {result.iterations} search {result.iterations === 1 ? "pass" : "passes"}</span>
                <span className="text-gray-400">{showPlan ? "↑" : "↓"}</span>
              </button>
              {showPlan && (
                <div className="px-4 py-3 space-y-2">
                  {result.sub_questions.map((q, i) => (
                    <div key={i} className="flex gap-3 text-sm text-gray-300">
                      <span className="text-gray-500 shrink-0">{i + 1}.</span>
                      <span>{q}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Report — card per section */}
            <div className="space-y-4">
              {splitReportIntoSections(result.report).map((section, idx) => (
                <div
                  key={idx}
                  className="border border-gray-800 rounded-lg overflow-hidden"
                >
                  <div className="px-4 py-3 bg-gray-900 text-sm font-medium">
                    {section.title}
                  </div>
                  <div className="px-4 py-4 [&_strong]:text-gray-100 [&_strong]:font-semibold">
                    <ReactMarkdown components={reportMarkdownComponents}>
                      {section.body}
                    </ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>

            {/* Sources */}
            <div className="border border-gray-800 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-900 text-sm font-medium">
                Sources · {result.sources.length}
              </div>
              <div className="px-4 py-3 space-y-2">
                {result.sources.map((source, i) => (
                  <a
                    key={i}
                    href={source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={"block text-sm text-blue-400 hover:text-blue-300 truncate transition-colors"}
                  >
                    {source}
                  </a>
                ))}
              </div>
            </div>

          </div>
        )}
      </div>
    </main>
  );
}