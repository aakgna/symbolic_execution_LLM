export interface TestCase {
	input: string;
	expected: string;
	actual: string;
	passed: boolean;
}

export interface TestCaseResults {
	total: number;
	passed: number;
	cases: TestCase[];
}

export interface CoverageLine {
	text: string;
	covered: boolean;
}

export interface CoverageResults {
	percentage: number;
	lines: CoverageLine[];
}

export interface DeadCodeInstance {
	line: number;
	code: string;
	reason: string;
}

export interface DeadCodeResults {
	found: boolean;
	instances: DeadCodeInstance[];
}

export interface AnalysisResult {
	testCases: TestCaseResults;
	coverage: CoverageResults;
	deadCode: DeadCodeResults;
}
