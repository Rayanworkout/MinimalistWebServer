import logging
import os

current_dir = os.path.dirname(__file__)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=os.path.join(current_dir, "logs.log"),  # Specify the log file
    filemode="a",  # persisting logs
)

# Create a logger
logger = logging.getLogger()
