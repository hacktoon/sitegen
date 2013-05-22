import os

# Configuration values
DATA_FILE = 'data.ion'

CONFIG_FILE = 'config.ion'
THEMES_DIR = 'themes'
MAIN_TEMPLATE = 'main.tpl'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Setting values based on config
script_path = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_path, 'data')

MODEL_RSS_FILE = os.path.join(data_dir, 'rss.tpl')
MODEL_CONFIG_FILE = os.path.join(data_dir, CONFIG_FILE)
MODEL_DATA_FILE = os.path.join(data_dir, DATA_FILE)
MODEL_THEMES_DIR = os.path.join(data_dir, THEMES_DIR)
