from src import client
from typing import List
from utils.fileio import read
from src.bot import get_cli_with_cogs
import json


def get_bots() -> List[client.Client]:
    """
    Returns a list of Bot objects from a db.json file
    """
    bots = []

    json_str = read("assets/multi_bot/db.json")
    prompt_header = read("assets/multi_bot/prompt_header.txt")

    data = json.loads(json_str)
    for item in data:
        name, description = item["name"], item["description"]
        prompt = f"{prompt_header}\nname: {name}\ndescription: {description}"
        bot = get_cli_with_cogs(token=item["token"], prompt=prompt)
        bots.append(bot)
    return bots
