"""
Tool 1: Code Executor
Topics covered:
  - Python tool calling  → exec() based safe code runner
  - Shell command tools  → subprocess for shell commands
"""

import io
import os
import sys
import json
import contextlib
import traceback
import subprocess
from typing import Dict, Any


class CodeExecutorTool:
    """
    Executes Python code strings and shell commands.
    Used by CodeAgent to run analysis on the dataset.
    """

    name        = "code_executor"
    description = "Executes Python code or shell commands and returns output"

    # ── Tool Schema (function-calling format) ────────────────────────
    schema = {
        "name": "code_executor",
        "description": "Run Python code or a shell command",
        "parameters": {
            "type": "object",
            "properties": {
                "python_code": {
                    "type": "string",
                    "description": "Python code string to execute"
                },
                "shell_command": {
                    "type": "string",
                    "description": "Shell command to run via subprocess"
                }
            }
        }
    }

    # ── Python execution ─────────────────────────────────────────────
    def run_python(self, code: str) -> Dict[str, Any]:
        """
        Execute a Python code string safely.
        Captures stdout. Returns status + output.
        """
        stdout_buf = io.StringIO()
        result     = {"status": "error", "output": "", "error": ""}

        try:
            with contextlib.redirect_stdout(stdout_buf):
                exec(compile(code, "<code_executor>", "exec"), {"__builtins__": __builtins__})
            result["status"] = "success"
            result["output"] = stdout_buf.getvalue()
        except Exception:
            result["error"] = traceback.format_exc()

        return result

    # ── Shell command execution ───────────────────────────────────────
    def run_shell(self, command: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Run a shell command via subprocess.
        Returns stdout, stderr, and return code.
        """
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "status":      "success" if proc.returncode == 0 else "error",
                "stdout":      proc.stdout.strip(),
                "stderr":      proc.stderr.strip(),
                "return_code": proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ── execute() — unified entry point ──────────────────────────────
    def execute(self, python_code: str = None, shell_command: str = None) -> Dict[str, Any]:
        if python_code:
            return self.run_python(python_code)
        if shell_command:
            return self.run_shell(shell_command)
        return {"status": "error", "error": "Provide python_code or shell_command"}

    # ── Pre-built analysis for Large_Agentic_AI_Applications_2025.csv ─
    def analyze_dataset(self, csv_path: str) -> Dict[str, Any]:
        """Run full pandas analysis on the Agentic AI dataset."""
        code = f"""
import pandas as pd
import json

df = pd.read_csv("{csv_path}")

analysis = {{
    "total_records":      int(len(df)),
    "total_columns":      int(len(df.columns)),
    "industries":         int(df["Industry"].nunique()),
    "application_areas":  int(df["Application Area"].nunique()),
    "tech_stacks":        int(df["Technology Stack"].nunique()),
    "top_industry":       df["Industry"].value_counts().idxmax(),
    "top_area":           df["Application Area"].value_counts().idxmax(),
    "top_tech_stack":     df["Technology Stack"].value_counts().idxmax(),
    "top_region":         df["Geographical Region"].value_counts().idxmax(),
    "peak_year":          int(df["Deployment Year"].value_counts().idxmax()),
    "industry_counts":    df["Industry"].value_counts().to_dict(),
    "area_counts":        df["Application Area"].value_counts().to_dict(),
    "year_counts":        df["Deployment Year"].value_counts().sort_index().to_dict(),
    "region_counts":      df["Geographical Region"].value_counts().to_dict(),
    "stack_counts":       df["Technology Stack"].value_counts().head(5).to_dict(),
}}
print(json.dumps(analysis, indent=2))
"""
        return self.run_python(code)

    def top_5_insights(self, csv_path: str) -> Dict[str, Any]:
        """Generate top 5 human-readable insights."""
        code = f"""
import pandas as pd

df = pd.read_csv("{csv_path}")

ind   = df["Industry"].value_counts()
area  = df["Application Area"].value_counts()
stack = df["Technology Stack"].value_counts()
reg   = df["Geographical Region"].value_counts()
yr    = df["Deployment Year"].value_counts().sort_index()

print(f"1. Total AI agents: {{len(df):,}} across {{df['Industry'].nunique()}} industries")
print(f"2. Top industry: {{ind.index[0]}} with {{ind.iloc[0]:,}} agents")
print(f"3. Top application area: {{area.index[0]}} with {{area.iloc[0]:,}} agents")
print(f"4. Most used tech stack: {{stack.index[0]}} ({{stack.iloc[0]:,}} uses)")
print(f"5. Top deployment region: {{reg.index[0]}} with {{reg.iloc[0]:,}} deployments")
"""
        return self.run_python(code)

    def industry_area_crosstab(self, csv_path: str) -> Dict[str, Any]:
        """Cross-tab of Industry vs Application Area."""
        code = f"""
import pandas as pd
df = pd.read_csv("{csv_path}")
pivot = pd.crosstab(df["Industry"], df["Application Area"])
print(pivot.to_string())
"""
        return self.run_python(code)

    def year_region_trend(self, csv_path: str) -> Dict[str, Any]:
        """Deployments per year broken down by region."""
        code = f"""
import pandas as pd
df    = pd.read_csv("{csv_path}")
trend = df.groupby(["Deployment Year", "Geographical Region"]).size().unstack(fill_value=0)
print(trend.to_string())
"""
        return self.run_python(code)

    def shell_file_info(self, csv_path: str) -> Dict[str, Any]:
        """Use shell commands to inspect the CSV file."""
        results = {}
        results["line_count"]   = self.run_shell(f"wc -l {csv_path}")
        results["file_size"]    = self.run_shell(f"du -sh {csv_path}")
        results["column_names"] = self.run_shell(f"head -1 {csv_path}")
        results["sample_rows"]  = self.run_shell(f"tail -3 {csv_path}")
        return results


# ── Demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tool     = CodeExecutorTool()
    csv_path = "data/Large_Agentic_AI_Applications_2025.csv"

    print("=" * 55)
    print("  TOPIC: Python Tool Calling")
    print("=" * 55)
    r = tool.top_5_insights(csv_path)
    print(r["output"] if r["status"] == "success" else r["error"])

    print("\n" + "=" * 55)
    print("  TOPIC: Shell Command Tools")
    print("=" * 55)
    shell_info = tool.shell_file_info(csv_path)
    for key, val in shell_info.items():
        print(f"\n[{key}]")
        print(val.get("stdout") or val.get("error"))

    print("\n" + "=" * 55)
    print("  Full Dataset Analysis (JSON)")
    print("=" * 55)
    r = tool.analyze_dataset(csv_path)
    print(r["output"] if r["status"] == "success" else r["error"])