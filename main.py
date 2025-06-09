import os

from client.client import Client
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    PREFIX = os.getenv("PREFIX")

    client = Client(prefix=PREFIX)
    client.run(TOKEN)
