import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
