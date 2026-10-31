from src.init_db import main as init_db
from src.pipeline import run_pipeline, counts
from src.logging_config import get_logger

if __name__ == "__main__":
    logger=get_logger(__name__)
    logger.info("Creating MySQL database and tables")
    init_db()
    print("Pipeline result:",run_pipeline())
    print("Table counts:",counts())
    print("Run `python -m src.insights` to view business insights.")
