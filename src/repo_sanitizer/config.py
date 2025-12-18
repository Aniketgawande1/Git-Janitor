import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "protected_branches": ["main", "master", "dev", "develop"],
    "auto_confirm": False,
    "dry_run_default": False,
    "log_file": "repo-sanitizer.log"
}

def load_config():
    cfg = Path(".repo-sanitizer.yml")
    if cfg.exists():
        with open(cfg) as f:
            return {**DEFAULT_CONFIG, **yaml.safe_load(f)}
    return DEFAULT_CONFIG
