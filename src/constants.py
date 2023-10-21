from pathlib import (
    Path,
)

BASE_DIR = Path(__file__).parent

MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = 'parser.log'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

DOWNLOAD_BLOCK_SIZE = 102400

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
