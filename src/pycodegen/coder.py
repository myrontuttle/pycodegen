import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


class Coder:
    """
    Coder Class
    """

    work_dir = Path("C:\\Users\\myron\\PycharmProjects")
    host = "https://github.com"
    owner = "myrontuttle"
