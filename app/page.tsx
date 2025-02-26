"use client";

import { useState } from "react";
import CodeEditor from "@/components/code-editor";
import AnalyticsPanel from "@/components/analytics-panel";
import { analyzeCode } from "@/app/actions";
import type { AnalysisResult } from "@/lib/types";

export default function Home() {
	const [code, setCode] = useState<string>(`def example(x):
    if x > 0:
        return x * 2
    return x  # This line will be covered
    print("This is dead code")  # This will be detected as dead code`);
	const [isAnalyzing, setIsAnalyzing] = useState(false);
	const [results, setResults] = useState<AnalysisResult | null>(null);

	const handleCodeChange = (newCode: string) => {
		setCode(newCode);
	};

	const handleAnalyze = async () => {
		setIsAnalyzing(true);
		try {
			const analysisResults = await analyzeCode(code);
			setResults(analysisResults);
		} catch (error) {
			console.error("Analysis failed:", error);
		} finally {
			setIsAnalyzing(false);
		}
	};

	return (
		<main className="flex min-h-screen flex-col">
			<header className="bg-primary p-4">
				<h1 className="text-2xl font-bold text-primary-foreground">
					Python Code Analyzer
				</h1>
			</header>

			<div className="flex flex-1 flex-col md:flex-row">
				<div className="w-full md:w-1/2 p-4 border-r border-border">
					<div className="flex justify-between items-center mb-2">
						<h2 className="text-xl font-semibold">Code Input</h2>
						<button
							onClick={handleAnalyze}
							disabled={isAnalyzing}
							className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
						>
							{isAnalyzing ? "Analyzing..." : "Analyze Code"}
						</button>
					</div>
					<CodeEditor code={code} onChange={handleCodeChange} />
				</div>

				<div className="w-full md:w-1/2 p-4">
					<h2 className="text-xl font-semibold mb-2">Code Analytics</h2>
					<AnalyticsPanel results={results} isLoading={isAnalyzing} />
				</div>
			</div>
		</main>
	);
}
