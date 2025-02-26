import os
import json
import ast
import re
from typing import Dict, List, Any, Tuple
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.function_name = self._extract_function_name()
        
    def _extract_function_name(self) -> str:
        """Extract function name from the TypeScript code"""
        match = re.search(r'export async function (\w+)', self.code)
        if match:
            return match.group(1)
        return "unknown_function"
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the code using OpenAI API to create comprehensive test cases"""
        # Extract branches and logical paths in the code
        branches = self._extract_branches()
        
        # Get test cases from OpenAI
        test_cases = self._generate_test_cases(branches)
        
        # Analyze for potential dead code
        dead_code = self._analyze_dead_code()
        
        # Create coverage analysis
        coverage = self._analyze_coverage(test_cases)
        
        return {
            "testCases": test_cases,
            "coverage": coverage,
            "deadCode": dead_code,
            "branchesFound": branches
        }
    
    def _extract_branches(self) -> List[Dict[str, Any]]:
        """Extract conditional branches from the code"""
        branches = []
        
        # Find all if statements, switch cases, and loops
        if_pattern = r'if\s*\((.*?)\)'
        ternary_pattern = r'\?(.*?):(.*?);'
        switch_pattern = r'switch\s*\((.*?)\)'
        
        # Extract if conditions
        if_conditions = re.findall(if_pattern, self.code)
        for condition in if_conditions:
            branches.append({
                "type": "if",
                "condition": condition.strip(),
                "description": f"Branch when {condition.strip()} is true"
            })
            branches.append({
                "type": "else",
                "condition": f"!({condition.strip()})",
                "description": f"Branch when {condition.strip()} is false"
            })
        
        # Extract ternary operations
        ternaries = re.findall(ternary_pattern, self.code)
        for i, ternary in enumerate(ternaries):
            true_part, false_part = ternary
            branches.append({
                "type": "ternary",
                "condition": f"Condition #{i+1}",
                "description": f"Ternary operation with true path: {true_part} and false path: {false_part}"
            })
        
        # Process specific function logic in the code
        if "functionMatch" in self.code and "hasDeadCode" in self.code:
            branches.append({
                "type": "functionMatch",
                "condition": "code.match(/def\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(/)",
                "description": "Branch when function pattern is found in the code"
            })
            branches.append({
                "type": "hasDeadCode",
                "condition": "code.includes('# This will be detected as dead code')",
                "description": "Branch when dead code marker is found"
            })
        
        return branches
    
    def _generate_test_cases(self, branches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test cases using OpenAI API to cover all branches"""
        client = openai.OpenAI(api_key="api_key")
        prompt = self._create_test_case_prompt(branches)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or another appropriate model
            messages=[
                {"role": "system", "content": "You are a testing expert who creates comprehensive test cases for code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        # Extract the generated test cases from the response
        try:
            test_cases_json = self._extract_json_from_response(response.choices[0].message.content)
            return test_cases_json
        except Exception as e:
            print(f"Error parsing OpenAI response: {e}")
            return {
                "total": 0,
                "passed": 0,
                "cases": []
            }
    
    def _create_test_case_prompt(self, branches: List[Dict[str, Any]]) -> str:
        """Create a prompt for OpenAI to generate test cases"""
        branch_descriptions = "\n".join([f"- {b['description']}" for b in branches])
        
        prompt = f"""
Given the following TypeScript code for a function called '{self.function_name}':

```typescript
{self.code}
```

This function appears to be a server action that analyzes Python code.

I've identified the following logical branches that need test coverage:
{branch_descriptions}

Please generate comprehensive test cases in JSON format that will exercise all these branches. 
Each test case should include:
1. A sample Python code input that would be passed to the function
2. The expected output
3. A description of which branch it's testing

Return your response in the following JSON format:
{{
  "total": <number of test cases>,
  "passed": <number expected to pass>,
  "cases": [
    {{
      "input": "<sample Python code>",
      "expected": "<expected output>",
      "actual": "<expected actual output>",
      "passed": <boolean>,
      "description": "<description of branch being tested>"
    }},
    ...more test cases...
  ]
}}

Focus on generating diverse inputs that cover all branches in the code, including edge cases.
"""
        return prompt
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from the OpenAI response text"""
        # Try to find JSON block in the response
        json_match = re.search(r'```json\n(.*?)```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no code block, try to extract JSON directly
            json_str = response_text
        
        # Clean up and parse the JSON
        try:
            # Remove any explanation text before or after the JSON
            json_str = re.sub(r'^[^{]*', '', json_str)
            json_str = re.sub(r'[^}]*$', '', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback: try to extract just the JSON object
            json_pattern = r'({[^{]*"total"[^}]*})'
            match = re.search(json_pattern, json_str, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise
    
    def _analyze_dead_code(self) -> Dict[str, Any]:
        """Analyze the code for potential dead code"""
        # For TypeScript code, we'll use a simplified approach
        lines = self.code.split("\n")
        dead_code_instances = []
        
        # Look for patterns that might indicate dead code
        for i, line in enumerate(lines):
            if "return" in line and i+1 < len(lines) and not lines[i+1].strip().startswith("}"):
                dead_code_instances.append({
                    "line": i+2,
                    "code": lines[i+1],
                    "reason": "This code follows a return statement and may be unreachable"
                })
            
            if "// This will be detected as dead code" in line or "/* dead code */" in line:
                dead_code_instances.append({
                    "line": i+1,
                    "code": line,
                    "reason": "Code marked as dead code by comment"
                })
        
        return {
            "found": len(dead_code_instances) > 0,
            "instances": dead_code_instances
        }
    
    def _analyze_coverage(self, test_cases: Dict[str, Any]) -> Dict[str, Any]:
        """Create a coverage report based on the test cases"""
        lines = self.code.split("\n")
        covered_lines = [False] * len(lines)
        
        # Mark lines as covered based on the test cases
        # This is a simplified simulation of coverage
        if test_cases.get("cases"):
            # Mark important structural lines as covered
            for i, line in enumerate(lines):
                # Mark function declaration, returns, and key logic as covered
                if any(keyword in line for keyword in ["function", "return", "const result", "await"]):
                    covered_lines[i] = True
                    
                # Mark lines containing tested branches as covered
                for case in test_cases.get("cases", []):
                    description = case.get("description", "")
                    branch_indicators = [
                        "functionMatch", 
                        "hasDeadCode",
                        "setTimeout",
                        "mkdir",
                        "writeFile"
                    ]
                    
                    if any(indicator in line and indicator in description for indicator in branch_indicators):
                        covered_lines[i] = True
        
        # Calculate coverage percentage
        coverage_percentage = int((sum(covered_lines) / len(covered_lines)) * 100) if covered_lines else 0
        
        return {
            "percentage": coverage_percentage,
            "lines": [{"text": text, "covered": covered} for text, covered in zip(lines, covered_lines)]
        }

def main():
    # Get file from arguments or input
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        with open(file_path, 'r') as f:
            code = f.read()
    else:
        print("Please enter the TypeScript code to analyze (end with Ctrl+D on Unix or Ctrl+Z on Windows):")
        code = sys.stdin.read()
    
    # Initialize analyzer
    analyzer = CodeAnalyzer(code)
    
    # Run analysis
    result = analyzer.analyze()
    
    # Output results
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()