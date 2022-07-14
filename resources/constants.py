
from pathlib import Path

RESOURCE_DIR = Path(__file__).parent.__str__() + '/'
LOG_DIR = RESOURCE_DIR + 'logs/'
CONFIG_FILE = RESOURCE_DIR + 'config.yaml'
REPORT_INDEX = RESOURCE_DIR + 'report/index.html'
PLOT_DIR = Path(__file__).parent.parent.__str__() + '/application/plotting/results/'
