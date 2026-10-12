"""Offline YAML syntax validation (no warehouse access)."""
from pathlib import Path
import yaml

paths = [
    Path("dbt_project.yml"),
    Path("profiles.yml.example"),
    Path("models/staging/_sources.yml"),
    Path("models/staging/_models.yml"),
    Path("models/intermediate/_models.yml"),
    Path("models/marts/_models.yml"),
]
for path in paths:
    with path.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    print(f"OK: {path}")
