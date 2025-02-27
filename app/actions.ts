"use server";

import type { AnalysisResult } from "@/lib/types";
import { writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { tmpdir } from "os";
import { v4 as uuidv4 } from "uuid";

export async function analyzeCode(code: string): Promise<AnalysisResult> {
	// create a temporary directory for analysis
	const tempDir = join(tmpdir(), `python-analysis-${uuidv4()}`);
	await mkdir(tempDir, { recursive: true });

	// write the code to the same file in the directory
	const codePath = join(tempDir, "code.py");
	await writeFile(codePath, code);

	try {
		const { execSync } = require("child_process");

		// FIXME: CHANGE METHOD FOR FILE PATH, IS LOCAL TO USER
		// FIXME: CHANGE METHOD FOR VENV ENV, IS LOCAL TO USER
		// execution sync, change buffer if necessary
		const analysisResult = execSync(
			`/Users/ultra/Desktop/symbolic_execution_LLM/myenv/bin/python3 /Users/njoby001/Desktop/symbolic_execution_LLM/api/analyze.py ${codePath}`,
			{
				encoding: "utf-8",
				maxBuffer: 1024 * 1024 * 10,
			}
		);

		// parse the JSON output from Python script
		const result: AnalysisResult = JSON.parse(analysisResult);
		console.log("Results:");
		console.log(result["coverage"]);
		return result;
	} catch (error) {
		console.error("Error running test case generation:", error);
		// add timeout
		await new Promise((resolve) => setTimeout(resolve, 1500));

		// we'll parse the code to find function name for test cases
		// if function name is not in the matches, call it unknown
		// afterwards, we can analyze that function to see which line is dead
		const functionMatch = code.match(/def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/);
		const functionName = functionMatch ? functionMatch[1] : "unknown_function";

		// generate mock analysis results
		const lines = code.split("\n");
		const hasDeadCode = code.includes("# This will be detected as dead code");


		// this is a SAMPLE analysis result we mocked up that will match the syntax when our program is actually being run
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
		
		// this is another sample one
		const result2: AnalysisResult = {
			testCases: {
				total: 4,
				passed: 1,
				cases: [
					{
						input: `${functionName}(10)`,
						expected: "20",
						actual: "20",
						passed: true,
					},
					{
						input: `${functionName}(0)`,
						expected: "0",
						actual: "-1",
						passed: false,
					},
					{
						input: `${functionName}(-5)`,
						expected: "-10",
						actual: "-5",
						passed: false,
					},
					{
						input: `${functionName}(1)`,
						expected: "1",
						actual: "-100",
						passed: false,
					},
				],
			},
			coverage: {
				percentage: 60,
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

	// Run Python analysis script
	// we need a Python script that can:
	// generate the test cases
	// runs the coverage analysis and output AST for analysis
	// detects dead code using AST analysis
}
