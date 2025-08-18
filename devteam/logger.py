import logging
from pathlib import Path

def setup_logger():
    log_file = Path(__file__).resolve().parent.parent / "devteam.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() # Also print to console
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()
