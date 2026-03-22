"""
Tool 3: File Agent
Topics covered:
  - File reading/writing  → read/write .txt, .csv, .json
  - Local search engine   → search files by name, content, keyword
"""

import os
import sys
import csv
import json
import glob
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class FileAgentTool:
    """
    Reads and writes .txt, .csv, .json files.
    Also provides a local search engine to find files
    and search content within the dataset.
    """

    name        = "file_agent"
    description = "Reads/writes files and searches local filesystem or CSV content"

    # ── Tool Schema ───────────────────────────────────────────────────
    schema = {
        "name": "file_agent",
        "description": "Read, write, or search files",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "search_files", "search_content"],
                    "description": "Action to perform"
                },
                "filepath": {
                    "type": "string",
                    "description": "Path to file for read/write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write"
                },
                "keyword": {
                    "type": "string",
                    "description": "Keyword for search actions"
                }
            },
            "required": ["action"]
        }
    }

    def __init__(self, base_dir: str = ".", output_dir: str = "output"):
        self.base_dir   = base_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ── Unified execute() ─────────────────────────────────────────────
    def execute(self, action: str, filepath: str = "",
                content: str = "", keyword: str = "") -> Dict[str, Any]:
        if action == "read":
            return self.read_file(filepath)
        elif action == "write":
            return self.write_file(filepath, content)
        elif action == "search_files":
            return self.search_files(keyword)
        elif action == "search_content":
            return self.search_csv_content(filepath, keyword)
        return {"success": False, "error": f"Unknown action: {action}"}

    # ─────────────────────────────────────────────────────────────────
    # TOPIC: File Reading
    # ─────────────────────────────────────────────────────────────────
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Auto-detect file type and read."""
        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}
        ext = Path(filepath).suffix.lower()
        if ext == ".csv":   return self.read_csv(filepath)
        if ext == ".json":  return self.read_json(filepath)
        return self.read_txt(filepath)

    def read_csv(self, filepath: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(filepath)
            return {
                "success": True,
                "rows":    len(df),
                "columns": list(df.columns),
                "data":    df.head(10).to_dict(orient="records"),
                "dtypes":  df.dtypes.astype(str).to_dict()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_txt(self, filepath: str) -> Dict[str, Any]:
        try:
            content = open(filepath, "r").read()
            return {"success": True, "content": content, "lines": content.count("\n") + 1}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_json(self, filepath: str) -> Dict[str, Any]:
        try:
            data = json.load(open(filepath, "r"))
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def summarize_csv(self, filepath: str) -> Dict[str, Any]:
        """Deep summary of the Agentic AI CSV."""
        try:
            df = pd.read_csv(filepath)
            return {
                "success":           True,
                "total_rows":        len(df),
                "columns":           list(df.columns),
                "industries":        df["Industry"].nunique(),
                "industry_counts":   df["Industry"].value_counts().to_dict(),
                "application_areas": df["Application Area"].nunique(),
                "area_counts":       df["Application Area"].value_counts().to_dict(),
                "deployment_years":  df["Deployment Year"].value_counts().sort_index().to_dict(),
                "regions":           df["Geographical Region"].value_counts().to_dict(),
                "top_tech_stacks":   df["Technology Stack"].value_counts().head(5).to_dict(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─────────────────────────────────────────────────────────────────
    # TOPIC: File Writing
    # ─────────────────────────────────────────────────────────────────
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Auto-detect file type and write."""
        ext = Path(filepath).suffix.lower()
        if ext == ".json":
            try:
                return self.write_json(filepath, json.loads(content))
            except Exception:
                pass
        return self.write_txt(filepath, content)

    def write_txt(self, filename: str, content: str) -> Dict[str, Any]:
        try:
            path = os.path.join(self.output_dir, os.path.basename(filename))
            open(path, "w").write(content)
            return {"success": True, "path": path, "bytes": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_csv(self, filename: str, data: List[Dict]) -> Dict[str, Any]:
        if not data:
            return {"success": False, "error": "No data provided"}
        try:
            path = os.path.join(self.output_dir, os.path.basename(filename))
            pd.DataFrame(data).to_csv(path, index=False)
            return {"success": True, "path": path, "rows": len(data)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_json(self, filename: str, data: Any) -> Dict[str, Any]:
        try:
            path = os.path.join(self.output_dir, os.path.basename(filename))
            json.dump(data, open(path, "w"), indent=2)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_report(self, filename: str, insights: List[str],
                     title: str = "ANALYSIS REPORT") -> Dict[str, Any]:
        """Write a formatted numbered insights report."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            title,
            f"Generated : {ts}",
            f"Dataset   : Large_Agentic_AI_Applications_2025.csv",
            "=" * 55,
            ""
        ]
        for i, ins in enumerate(insights, 1):
            lines.append(f"{i}. {ins}")
        lines.append("")
        return self.write_txt(filename, "\n".join(lines))

    # ─────────────────────────────────────────────────────────────────
    # TOPIC: Local Search Engine
    # ─────────────────────────────────────────────────────────────────
    def search_files(self, keyword: str,
                     search_dir: str = ".",
                     extensions: List[str] = None) -> Dict[str, Any]:
        """
        Search local filesystem for files matching a keyword in name.
        Acts as a local search engine over the project directory.
        """
        if extensions is None:
            extensions = [".csv", ".txt", ".json", ".py", ".md"]

        matches = []
        try:
            for ext in extensions:
                pattern = os.path.join(search_dir, "**", f"*{keyword}*{ext}")
                for filepath in glob.glob(pattern, recursive=True):
                    stat = os.stat(filepath)
                    matches.append({
                        "file":     filepath,
                        "size_kb":  round(stat.st_size / 1024, 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    })
            return {"success": True, "matches": matches, "count": len(matches)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_csv_content(self, filepath: str,
                           keyword: str,
                           columns: List[str] = None) -> Dict[str, Any]:
        """
        Search inside a CSV file for rows containing a keyword.
        Local search engine over CSV content.
        """
        try:
            df = pd.read_csv(filepath)

            if columns:
                search_cols = [c for c in columns if c in df.columns]
            else:
                search_cols = df.columns.tolist()

            mask = df[search_cols].apply(
                lambda col: col.astype(str).str.contains(keyword, case=False, na=False)
            ).any(axis=1)

            results = df[mask]
            return {
                "success":  True,
                "keyword":  keyword,
                "matches":  len(results),
                "data":     results.head(20).to_dict(orient="records")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_by_column(self, filepath: str,
                         column: str, value: str) -> Dict[str, Any]:
        """Filter CSV rows where column == value."""
        try:
            df       = pd.read_csv(filepath)
            filtered = df[df[column] == value]
            return {
                "success": True,
                "column":  column,
                "value":   value,
                "matches": len(filtered),
                "data":    filtered.head(20).to_dict(orient="records")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, directory: str = ".") -> Dict[str, Any]:
        """List all files in a directory recursively — local file index."""
        try:
            file_index = []
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in ["venv", "__pycache__", ".git"]]
                for fname in files:
                    path = os.path.join(root, fname)
                    stat = os.stat(path)
                    file_index.append({
                        "path":     path,
                        "name":     fname,
                        "ext":      Path(fname).suffix,
                        "size_kb":  round(stat.st_size / 1024, 2)
                    })
            return {"success": True, "files": file_index, "count": len(file_index)}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ── Demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tool     = FileAgentTool(base_dir=".", output_dir="output")
    csv_path = "data/Large_Agentic_AI_Applications_2025.csv"

    print("=" * 55)
    print("  TOPIC: File Reading")
    print("=" * 55)
    r = tool.read_csv(csv_path)
    if r["success"]:
        print(f"  Rows    : {r['rows']:,}")
        print(f"  Columns : {r['columns']}")

    print("\n" + "=" * 55)
    print("  TOPIC: File Writing")
    print("=" * 55)
    r = tool.write_report("demo_report.txt", [
        "Dataset has 10,000 records",
        "Top industry: Transportation",
        "Top tech stack: IoT, ML",
    ], title="DEMO REPORT")
    print(f"  Written to: {r.get('path')}")

    print("\n" + "=" * 55)
    print("  TOPIC: Local Search Engine — File Search")
    print("=" * 55)
    r = tool.search_files("agentic", search_dir=".")
    print(f"  Files matching 'agentic': {r['count']}")
    for f in r["matches"]:
        print(f"    {f['file']}  ({f['size_kb']} KB)")

    print("\n" + "=" * 55)
    print("  TOPIC: Local Search Engine — CSV Content Search")
    print("=" * 55)
    r = tool.search_csv_content(csv_path, "fraud")
    print(f"  Rows matching 'fraud': {r['matches']}")
    if r["data"]:
        print(f"  Sample: {r['data'][0]}")

    print("\n" + "=" * 55)
    print("  Filter by Industry: Healthcare")
    print("=" * 55)
    r = tool.search_by_column(csv_path, "Industry", "Healthcare")
    print(f"  Healthcare agents: {r['matches']}")