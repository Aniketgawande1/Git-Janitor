import logging
from .config import load_config

cfg = load_config()

logging.basicConfig(
    filename=cfg["log_file"],
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("repo-sanitizer")
