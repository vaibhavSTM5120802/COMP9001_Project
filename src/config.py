# src/config.py  -- Read the files for shortcuts
from pathlib import Path
import yaml

def load_shortcuts(path: Path):
    with path.open("r", encoding="utf-8") as f:                                                 #check for the file 
        data = yaml.safe_load(f)
    if not data or "apps" not in data or "meet" not in data["apps"]:                           # basic checks if important keys are present or not (meet)
        raise ValueError(f"Invalid or empty YAML at: {path}")
    return data

