"use server";

import type { AnalysisResult } from "@/lib/types";
import { writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { tmpdir } from "os";
import { v4 as uuidv4 } from "uuid";

export async function analyzeCode(code: string): Promise<AnalysisResult> {
	// Create a temporary directory for analysis
	const tempDir = join(tmpdir(), `python-analysis-${uuidv4()}`);
	await mkdir(tempDir, { recursive: true });

	// Write the code to a file
	const codePath = join(tempDir, "code.py");
	await writeFile(codePath, code);

	// Run Python analysis script
	// In a real implementation, you would have a Python script that:
	// 1. Generates test cases
	// 2. Runs coverage analysis
	// 3. Detects dead code using AST analysis

	// For this demo, we'll simulate the analysis results
	// In a real implementation, you would run a Python script and parse its output

	// Simulate a delay for analysis
	await new Promise((resolve) => setTimeout(resolve, 1500));

	// Parse code to find function name for test cases
	const functionMatch = code.match(/def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/);
	const functionName = functionMatch ? functionMatch[1] : "unknown_function";

	// Generate mock analysis results
	const lines = code.split("\n");
	const hasDeadCode = code.includes("# This will be detected as dead code");

	const result: AnalysisResult = {
		testCases: {
			total: 3,
			passed: 2,
			cases: [
				{
					input: `${functionName}(5)`,
					expected: "10",
					actual: "10",
					passed: true,
				},
				{
					input: `${functionName}(0)`,
					expected: "0",
					actual: "0",
					passed: true,
				},
				{
					input: `${functionName}(-5)`,
					expected: "-10",
					actual: "-5",
					passed: false,
				},
			],
		},
		coverage: {
			percentage: 80,
			lines: lines.map((text, index) => ({
				text,
				covered: !text.includes("dead code"),
			})),
		},
		deadCode: {
			found: hasDeadCode,
			instances: hasDeadCode
				? [
						{
							line: lines.findIndex((line) => line.includes("dead code")) + 1,
							code: lines.find((line) => line.includes("dead code")) || "",
							reason:
								"This code is unreachable because it follows a return statement",
						},
				  ]
				: [],
		},
	};

	return result;
}
