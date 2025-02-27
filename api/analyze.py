import os
import json
import ast
import re
from typing import Dict, List, Any, Tuple
import openai
from dotenv import load_dotenv

load_dotenv()

# configure OpenAI API
# FIXME: NEED TO ADD ANOTHER METHOD BESIDES API KEY
# CodeAnalyzer should analyze teh code with API to create the tests

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.function_name = self._extract_function_name()

    # find match and return, if not return unknown    
    def _extract_function_name(self) -> str:
        match = re.search(r'export async function (\w+)', self.code)
        if match:
            return match.group(1)
        return "unknown_function"
    
    # extract branches and get the test cases from OpenAI
    # find dead code and create coverage
    # return dictionary of strings that hold the branches
    # should have test cases, coverage, the dead code
    # and total branches that were found
    def analyze(self) -> Dict[str, Any]:
        branches = self._extract_branches()
        test_cases = self._generate_test_cases(branches)
        
        # find potential dead code
        dead_code = self._analyze_dead_code()
        coverage = self._analyze_coverage(test_cases)
        
        return {
            "testCases": test_cases,
            "coverage": coverage,
            "deadCode": dead_code,
            "branchesFound": branches
        }
    
    # helper function to extract conditional branches from code
    # FIXED: move if statement, switch cases, and loops here
    # FIXME: add checks for switch patterns
    def _extract_branches(self) -> List[Dict[str, Any]]:
        branches = []
        if_pattern = r'if\s*\((.*?)\)'
        ternary_pattern = r'\?(.*?):(.*?);'
        switch_pattern = r'switch\s*\((.*?)\)'
        
        # extract if conditions
        # FIXME: add extraction for if else statements
        # logic should be 'separate branch'
        # include the parameter?
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
        
        # extract ternary operations
        ternaries = re.findall(ternary_pattern, self.code)
        for i, ternary in enumerate(ternaries):
            true_part, false_part = ternary
            branches.append({
                "type": "ternary",
                "condition": f"Condition #{i+1}",
                "description": f"Ternary operation with true path: {true_part} and false path: {false_part}"
            })
        
        # if condition to process specific function logic within code
        # basically check which branch is true when function is found
        # or which code is dead, so that branch never executes
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
    
    # From here, we can use OpenAI's API to create the test cases
    def _generate_test_cases(self, branches: List[Dict[str, Any]]) -> Dict[str, Any]:
        client = openai.OpenAI(api_key="api_key")
        prompt = self._create_test_case_prompt(branches)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # FIXME: too broke for this model
            # FIXED: Change prompt, make it so GPT actually understands the syntax we want
            messages=[
                {"role": "system", "content": "You are a testing expert who creates comprehensive test cases for code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        # extract test cases from response
        # find total cases, and which ones passed
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
    
    # OPENAI is going to give a JSON file back, which we need to extract and analyze
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        
        json_match = re.search(r'```json\n(.*?)```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no code block, extract JSON directly
            json_str = response_text
        
        # clean up
        # parse JSON
        try:
            # FIXED: removing any extra text that GPT gives
            json_str = re.sub(r'^[^{]*', '', json_str)
            json_str = re.sub(r'[^}]*$', '', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            # if that doesn't work, try to extract only the JSON object
            json_pattern = r'({[^{]*"total"[^}]*})'
            match = re.search(json_pattern, json_str, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise
    
    # analyze the code for potential dead code
    def _analyze_dead_code(self) -> Dict[str, Any]:
        lines = self.code.split("\n")
        dead_code_instances = []
        
        # find patterns that could indicate dead code
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
    
    # create the coverage report from test cases
    # mark lines as covered based on the test cases
    def _analyze_coverage(self, test_cases: Dict[str, Any]) -> Dict[str, Any]:
        lines = self.code.split("\n")
        covered_lines = [False] * len(lines)
        
        if test_cases.get("cases"):
            #structural lines
            for i, line in enumerate(lines):
                #function declaration, returns, and key logic
                if any(keyword in line for keyword in ["function", "return", "const result", "await"]):
                    covered_lines[i] = True
                    
                # covered tested branches
                for case in test_cases.get("cases", []):
                    description = case.get("description", "")
                    branch_indicators = [
                        "functionMatch", 
                        "hasDeadCode",
                        "setTimeout",
                        "mkdir",
                        "writeFile"
                    ]
                    
                    #  mark as true so we can iterate and find percentage
                    if any(indicator in line and indicator in description for indicator in branch_indicators):
                        covered_lines[i] = True
        
        # find and return the coverage percentage
        coverage_percentage = int((sum(covered_lines) / len(covered_lines)) * 100) if covered_lines else 0
        
        return {
            "percentage": coverage_percentage,
            "lines": [{"text": text, "covered": covered} for text, covered in zip(lines, covered_lines)]
        }

def main():
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        with open(file_path, 'r') as f:
            code = f.read()
    else:
        print("Please enter the TypeScript code to analyze (end with Ctrl+D on Unix or Ctrl+Z on Windows):")
        code = sys.stdin.read()
    analyzer = CodeAnalyzer(code)
    result = analyzer.analyze()
    
    # output
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
