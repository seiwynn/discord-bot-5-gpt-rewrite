
from dotenv import load_dotenv
import asyncio

import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now you can import the module
from src.client import Client
# rest of your code
load_dotenv()


async def hello_world():
    client = Client("no-token-needed", "roleplay as a cat.")
    print(await client.chat("*pat head*"))
    print(await client.chat("hello!"))
# Run the function

asyncio.run(hello_world())
