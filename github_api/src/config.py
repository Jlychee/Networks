import os

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')

BASE_URL = "https://api.github.com"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
