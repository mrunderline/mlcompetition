from dotenv import load_dotenv
import os
import pathlib

load_dotenv()


DB_URL = os.getenv('DB_URL', 'mlcompetition.sqlite')

APP_SECRET_KEY = os.getenv('APP_SECRET_KEY', 'some_secret_key')
APP_ROOT_PATH = str(pathlib.Path(__file__).parent.absolute())

ALLOWED_EXTENSIONS = ['csv']
COMPETITION_FOLDER = os.getenv('COMPETITION_FOLDER', APP_ROOT_PATH + os.path.sep + 'competitions')
COMPETITION_SECRET_KEY = os.getenv('COMPETITION_SECRET_KEY', 'competition_secret_key')
