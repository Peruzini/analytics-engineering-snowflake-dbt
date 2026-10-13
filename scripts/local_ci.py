"""Offline-first dbt quality checks for Windows, without cloud usage."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".local-evidence" / "latest.json"

def call(report, name, command, env=None):
    print("\n=== " + name + " ===", flush=True)
    try:
        rc = subprocess.run(command, cwd=ROOT, env=env, check=False).returncode
    except OSError as err:
        rc = -1
        print(f"Missing executable: {err}", file=sys.stderr)
    report["steps"].append({"name": name, "exit_code": rc, "status": "PASS" if rc == 0 else "FAIL"})
    if rc:
        raise RuntimeError(f"{name} failed with exit code {rc}")

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()

def hashes():
    paths = [ROOT / x for x in ("dbt_project.yml", "requirements.txt", "profiles.yml.example")]
    for folder, pattern in (("seeds", "*.csv"), ("models", "*.sql"), ("models", "*.yml"),
                            ("snapshots", "*.yml"), ("tests/dbt", "*.sql"),
                            ("tests", "test_*.py"), ("scripts", "*.py"),
                            ("scripts", "market_config.json"), ("powerbi/data", "*.csv"),
                            ("powerbi", "*.pbip"), ("powerbi", "*.pbism"),
                            ("powerbi", "*.pbir"), ("powerbi", "*.bim"),
                            ("powerbi", "*.json")):
        paths += list((ROOT / folder).rglob(pattern))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths)) if p.is_file() and ".pbi" not in p.parts}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="Python, fixtures, YAML only (default)")
    group.add_argument("--full", action="store_true", help="Also parse Snowflake and run all dbt models locally in DuckDB")
    parser.add_argument("--publish", action="store_true", help="Stage successful full-run JSON for manual Git commit")
    args = parser.parse_args()
    if args.publish and not args.full:
        parser.error("--publish requires --full")
    report = {"schema_version": 1, "mode": "full" if args.full else "quick",
              "executed_at_utc": datetime.now(timezone.utc).isoformat(),
              "git_head": git("rev-parse", "HEAD"), "status": "LOCAL_VALIDATION_FAILED",
              "snowflake_queries_executed": False, "github_hosted_runner_used": False,
              "python_version": sys.version.split()[0], "source_sha256": hashes(), "steps": []}
    try:
        call(report, "seed-drift", [sys.executable, "scripts/generate_data.py", "--output-dir", "seeds", "--check"])
        call(report, "python-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
        call(report, "yaml", [sys.executable, "scripts/validate_yaml.py"])
        if args.full:
            dbt = shutil.which("dbt")
            if not dbt:
                raise RuntimeError("dbt not installed. Run: python -m pip install -r requirements.txt")
            with tempfile.TemporaryDirectory(prefix="ae-local-") as tempdir:
                temp = Path(tempdir)
                snow = temp / "snow"
                snow.mkdir()
                shutil.copyfile(ROOT / "profiles.yml.example", snow / "profiles.yml")
                safe = dict(os.environ)
                safe.update({
                    "DBT_SNOWFLAKE_ACCOUNT": "offline-placeholder",
                    "DBT_SNOWFLAKE_USER": "offline-placeholder",
                    "DBT_SNOWFLAKE_PRIVATE_KEY_PATH": str(temp / "no-key.p8"),
                    "DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE": "offline-placeholder",
                    "DBT_SNOWFLAKE_ROLE": "TRANSFORMER",
                    "DBT_SNOWFLAKE_DATABASE": "PORTFOLIO_DB",
                    "DBT_SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
                    "DBT_SNOWFLAKE_SCHEMA": "DBT_LOCAL",
                })
                call(report, "snowflake-offline-parse",
                     [dbt, "parse", "--profiles-dir", str(snow), "--no-partial-parse"], safe)
                local = temp / "duck"
                local.mkdir()
                (local / "profiles.yml").write_text(
                    "ae_snowflake_portfolio:\n"
                    "  target: local\n"
                    "  outputs:\n"
                    "    local:\n"
                    "      type: duckdb\n"
                    f"      path: {json.dumps((temp / 'portfolio.duckdb').as_posix())}\n"
                    "      schema: ae_local\n"
                    "      threads: 2\n", encoding="utf-8")
                opts = ["--profiles-dir", str(local), "--target", "local"]
                for name, command in (
                    ("duckdb-seed", ["seed"]),
                    ("duckdb-run", ["run"]),
                    ("duckdb-incremental-rerun", ["run", "--select", "fct_orders"]),
                    ("duckdb-snapshot", ["snapshot"]),
                    ("duckdb-tests", ["test"]),
                ):
                    call(report, name, [dbt, *command, *opts])
                call(report, "duckdb-powerbi-parity", [
                    sys.executable, "scripts/export_powerbi.py", "--check",
                    "--duckdb-path", str(temp / "portfolio.duckdb"),
                ])
        report["status"] = "LOCAL_FULL_PASS" if args.full else "LOCAL_QUICK_PASS"
    except Exception as exc:
        print(f"LOCAL_VALIDATION_FAILED: {exc}", file=sys.stderr)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']} | report: {OUTPUT}", flush=True)
    if report["status"] == "LOCAL_VALIDATION_FAILED":
        return 1
    if args.publish:
        if git("status", "--porcelain", "--untracked-files=normal"):
            print("EVIDENCE_BLOCKED: commit source changes first (dirty worktree)", file=sys.stderr)
            return 1
        dest = ROOT / "docs" / "evidence" / "local-validation"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / (report["git_head"][:12] + ".json")
        if path.exists():
            print("EVIDENCE_BLOCKED: report already exists for this source commit", file=sys.stderr)
            return 1
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        print(f"GIT_EVIDENCE_READY: {path.relative_to(ROOT)} (commit manually)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
