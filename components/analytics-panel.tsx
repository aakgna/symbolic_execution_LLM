"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { AnalysisResult } from "@/lib/types";
import { AlertCircle, CheckCircle2, XCircle } from "lucide-react";

interface AnalyticsPanelProps {
	results: AnalysisResult | null;
	isLoading: boolean;
}

export default function AnalyticsPanel({
	results,
	isLoading,
}: AnalyticsPanelProps) {
	const [activeTab, setActiveTab] = useState("test-cases");

	if (isLoading) {
		return (
			<div className="h-[500px] border border-border rounded-md bg-muted flex items-center justify-center">
				<div className="text-center">
					<div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
					<p className="text-muted-foreground">Analyzing your code...</p>
				</div>
			</div>
		);
	}

	if (!results) {
		return (
			<div className="h-[500px] border border-border rounded-md bg-muted flex items-center justify-center">
				<div className="text-center max-w-md px-4">
					<AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
					<h3 className="text-lg font-medium mb-2">No Analysis Results</h3>
					<p className="text-muted-foreground">
						Click the Analyze Code button to run tests, check coverage, and
						detect dead code in your Python script.
					</p>
				</div>
			</div>
		);
	}

	return (
		<Tabs
			value={activeTab}
			onValueChange={setActiveTab}
			className="h-[500px] border border-border rounded-md"
		>
			<TabsList className="grid grid-cols-3 w-full">
				<TabsTrigger value="test-cases">Test Cases</TabsTrigger>
				<TabsTrigger value="coverage">Line Coverage</TabsTrigger>
				<TabsTrigger value="dead-code">Dead Code</TabsTrigger>
			</TabsList>

			<TabsContent
				value="test-cases"
				className="p-4 h-[calc(500px-45px)] overflow-auto"
			>
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center justify-between">
							<span>Test Results</span>
							<span className="text-sm font-normal">
								{results.testCases.passed}/{results.testCases.total} Passed
							</span>
						</CardTitle>
						<CardDescription>
							Automatically generated test cases for your code
						</CardDescription>
					</CardHeader>
					<CardContent>
						<ul className="space-y-2">
							{results.testCases.cases.map((testCase, index) => (
								<li key={index} className="p-3 border border-border rounded-md">
									<div className="flex items-start">
										{testCase.passed ? (
											<CheckCircle2 className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
										) : (
											<XCircle className="h-5 w-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
										)}
										<div>
											<div className="font-medium">Test #{index + 1}</div>
											<div className="text-sm text-muted-foreground mt-1">
												<div>
													<span className="font-medium">Input:</span>{" "}
													{testCase.input}
												</div>
												<div>
													<span className="font-medium">Expected:</span>{" "}
													{testCase.expected}
												</div>
												{!testCase.passed && (
													<div>
														<span className="font-medium">Actual:</span>{" "}
														{testCase.actual}
													</div>
												)}
											</div>
										</div>
									</div>
								</li>
							))}
						</ul>
					</CardContent>
				</Card>
			</TabsContent>

			<TabsContent
				value="coverage"
				className="p-4 h-[calc(500px-45px)] overflow-auto"
			>
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center justify-between">
							<span>Line Coverage</span>
							<span className="text-sm font-normal">
								{results.coverage.percentage}%
							</span>
						</CardTitle>
						<CardDescription>
							Percentage of code lines executed during tests
						</CardDescription>
					</CardHeader>
					<CardContent>
						<Progress
							value={results.coverage.percentage}
							className="h-2 mb-4"
						/>

						<div className="border border-border rounded-md overflow-hidden mt-4">
							<div className="bg-muted px-4 py-2 font-mono text-sm">
								Code Coverage by Line
							</div>
							<div className="p-4 font-mono text-sm whitespace-pre">
								{results.coverage.lines.map((line, index) => (
									<div
										key={index}
										className={`flex ${
											line.covered ? "text-green-500" : "text-red-500"
										}`}
									>
										<span className="w-8 text-right mr-4 text-muted-foreground">
											{index + 1}
										</span>
										<span>{line.text}</span>
									</div>
								))}
							</div>
						</div>
					</CardContent>
				</Card>
			</TabsContent>

			<TabsContent
				value="dead-code"
				className="p-4 h-[calc(500px-45px)] overflow-auto"
			>
				<Card>
					<CardHeader>
						<CardTitle>Dead Code Analysis</CardTitle>
						<CardDescription>Code that can never be executed</CardDescription>
					</CardHeader>
					<CardContent>
						{results.deadCode.found ? (
							<div>
								<div className="mb-4 text-amber-500 flex items-center">
									<AlertCircle className="h-5 w-5 mr-2" />
									<span>
										Found {results.deadCode.instances.length} instances of dead
										code
									</span>
								</div>

								<ul className="space-y-3">
									{results.deadCode.instances.map((instance, index) => (
										<li
											key={index}
											className="border border-border rounded-md p-3"
										>
											<div className="font-medium mb-1">
												Line {instance.line}
											</div>
											<div className="font-mono text-sm bg-muted p-2 rounded-md">
												{instance.code}
											</div>
											<div className="text-sm text-muted-foreground mt-2">
												{instance.reason}
											</div>
										</li>
									))}
								</ul>
							</div>
						) : (
							<div className="flex items-center text-green-500">
								<CheckCircle2 className="h-5 w-5 mr-2" />
								<span>No dead code detected</span>
							</div>
						)}
					</CardContent>
				</Card>
			</TabsContent>
		</Tabs>
	);
}
