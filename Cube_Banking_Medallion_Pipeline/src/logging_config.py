import logging
from src.config import LOG_DIR

def get_logger(name="banking_pipeline"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        for handler in (
            logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ):
            handler.setFormatter(fmt)
            logger.addHandler(handler)
    return logger
