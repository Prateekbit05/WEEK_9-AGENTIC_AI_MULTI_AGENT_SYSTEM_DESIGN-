"""
Tool 2: DB Agent
Topics covered:
  - SQLite / CSV querying → loads CSV into SQLite, runs SQL queries
"""

import os
import sys
import sqlite3
import pandas as pd
from typing import Dict, Any, List


class DBAgentTool:
    """
    Loads Large_Agentic_AI_Applications_2025.csv into SQLite
    and executes SQL queries against it.

    Table: agentic_applications
    Columns:
        Industry, Application Area, AI Agent Name,
        Task Description, Technology Stack,
        Outcome Metrics, Deployment Year, Geographical Region
    """

    name        = "db_agent"
    description = "Queries the Agentic AI Applications SQLite database using SQL"

    # ── Tool Schema ───────────────────────────────────────────────────
    schema = {
        "name": "db_agent",
        "description": "Run SQL queries on the Agentic AI Applications database",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "SQL SELECT statement to execute"
                }
            },
            "required": ["sql"]
        }
    }

    def __init__(self, db_path: str = "data/agentic_ai.db"):
        self.db_path = db_path
        self.conn    = None

    # ── Connection ────────────────────────────────────────────────────
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # ── Load CSV → SQLite ─────────────────────────────────────────────
    def load_csv(self, csv_path: str) -> Dict[str, Any]:
        """
        Load CSV file into SQLite table 'agentic_applications'.
        Also creates summary tables for quick lookups.
        """
        if not os.path.exists(csv_path):
            return {"success": False, "error": f"CSV not found: {csv_path}"}

        try:
            df = pd.read_csv(csv_path)
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            df.to_sql("agentic_applications", conn, if_exists="replace", index=False)

            # Summary tables
            conn.execute("DROP TABLE IF EXISTS industry_summary")
            conn.execute("""
                CREATE TABLE industry_summary AS
                SELECT Industry,
                       COUNT(*) as agent_count
                FROM agentic_applications
                GROUP BY Industry
                ORDER BY agent_count DESC
            """)

            conn.execute("DROP TABLE IF EXISTS area_summary")
            conn.execute("""
                CREATE TABLE area_summary AS
                SELECT "Application Area",
                       COUNT(*) as agent_count
                FROM agentic_applications
                GROUP BY "Application Area"
                ORDER BY agent_count DESC
            """)

            conn.execute("DROP TABLE IF EXISTS stack_summary")
            conn.execute("""
                CREATE TABLE stack_summary AS
                SELECT "Technology Stack",
                       COUNT(*) as usage_count
                FROM agentic_applications
                GROUP BY "Technology Stack"
                ORDER BY usage_count DESC
            """)

            conn.commit()
            conn.close()

            return {
                "success":  True,
                "rows":     len(df),
                "columns":  list(df.columns),
                "db_path":  self.db_path,
                "tables":   ["agentic_applications", "industry_summary",
                             "area_summary", "stack_summary"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Core SQL query ────────────────────────────────────────────────
    def execute(self, sql: str) -> Dict[str, Any]:
        """Run any SQL statement. Returns rows as list of dicts."""
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows   = [dict(r) for r in cursor.fetchall()]
            return {"success": True, "data": rows, "count": len(rows)}
        except Exception as e:
            return {"success": False, "error": str(e), "data": []}

    # ── Pre-built queries (all matching actual CSV columns) ───────────

    def top_industries(self, limit: int = 10) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT Industry, COUNT(*) as agent_count
            FROM agentic_applications
            GROUP BY Industry
            ORDER BY agent_count DESC
            LIMIT {limit}
        """)

    def top_application_areas(self, limit: int = 10) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT "Application Area", COUNT(*) as count
            FROM agentic_applications
            GROUP BY "Application Area"
            ORDER BY count DESC
            LIMIT {limit}
        """)

    def deployments_by_year(self) -> Dict[str, Any]:
        return self.execute("""
            SELECT "Deployment Year", COUNT(*) as deployments
            FROM agentic_applications
            GROUP BY "Deployment Year"
            ORDER BY "Deployment Year"
        """)

    def deployments_by_region(self) -> Dict[str, Any]:
        return self.execute("""
            SELECT "Geographical Region", COUNT(*) as count
            FROM agentic_applications
            GROUP BY "Geographical Region"
            ORDER BY count DESC
        """)

    def top_tech_stacks(self, limit: int = 10) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT "Technology Stack", COUNT(*) as usage_count
            FROM agentic_applications
            GROUP BY "Technology Stack"
            ORDER BY usage_count DESC
            LIMIT {limit}
        """)

    def industry_area_breakdown(self, limit: int = 20) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT Industry, "Application Area", COUNT(*) as count
            FROM agentic_applications
            GROUP BY Industry, "Application Area"
            ORDER BY count DESC
            LIMIT {limit}
        """)

    def agents_by_year_and_region(self) -> Dict[str, Any]:
        return self.execute("""
            SELECT "Deployment Year", "Geographical Region", COUNT(*) as count
            FROM agentic_applications
            GROUP BY "Deployment Year", "Geographical Region"
            ORDER BY "Deployment Year", count DESC
        """)

    def search_by_task(self, keyword: str, limit: int = 10) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT "AI Agent Name", Industry, "Task Description", "Outcome Metrics"
            FROM agentic_applications
            WHERE "Task Description" LIKE '%{keyword}%'
            LIMIT {limit}
        """)

    def filter_by_industry(self, industry: str, limit: int = 10) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT "AI Agent Name", "Application Area",
                   "Technology Stack", "Outcome Metrics", "Deployment Year"
            FROM agentic_applications
            WHERE Industry = '{industry}'
            LIMIT {limit}
        """)

    def filter_by_year(self, year: int, limit: int = 10) -> Dict[str, Any]:
        return self.execute(f"""
            SELECT "AI Agent Name", Industry, "Application Area",
                   "Technology Stack", "Geographical Region"
            FROM agentic_applications
            WHERE "Deployment Year" = {year}
            LIMIT {limit}
        """)

    def stack_by_industry(self) -> Dict[str, Any]:
        return self.execute("""
            SELECT Industry, "Technology Stack", COUNT(*) as count
            FROM agentic_applications
            GROUP BY Industry, "Technology Stack"
            ORDER BY Industry, count DESC
        """)


# ── Demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tool = DBAgentTool(db_path="data/agentic_ai.db")

    print("=" * 55)
    print("  TOPIC: SQLite / CSV Querying")
    print("=" * 55)

    # Step 1: Load CSV into SQLite
    print("\n[1] Loading CSV into SQLite...")
    r = tool.load_csv("data/Large_Agentic_AI_Applications_2025.csv")
    if r["success"]:
        print(f"    ✓ Loaded {r['rows']:,} rows → {r['db_path']}")
        print(f"    ✓ Tables created: {r['tables']}")
    else:
        print(f"    ✗ {r['error']}")
        exit(1)

    tool.connect()

    queries = {
        "Top 5 Industries":       tool.top_industries(5),
        "Top 5 App Areas":        tool.top_application_areas(5),
        "Deployments by Year":    tool.deployments_by_year(),
        "Deployments by Region":  tool.deployments_by_region(),
        "Top 5 Tech Stacks":      tool.top_tech_stacks(5),
        "Top Industry+Area Combos": tool.industry_area_breakdown(5),
    }

    for title, result in queries.items():
        print(f"\n[{title}]")
        if result["success"]:
            for row in result["data"]:
                print(f"    {dict(row)}")
        else:
            print(f"    ERROR: {result['error']}")

    # Custom SQL query example
    print("\n[Custom SQL Query]")
    r = tool.execute("""
        SELECT Industry, COUNT(*) as count
        FROM agentic_applications
        WHERE "Deployment Year" = 2025
        GROUP BY Industry
        ORDER BY count DESC
        LIMIT 5
    """)
    for row in r["data"]:
        print(f"    {row}")

    tool.close()