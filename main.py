import os
from src import bot
from dotenv import load_dotenv
import logging
from utils.fileio import read


def check_library_versions() -> None:
    # TODO: check library versions based on requirements.txt
    pass


if __name__ == '__main__':
    check_library_versions()
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    prompt_location = "assets/sample_prompt.txt"

    try:
        prompt = read(prompt_location)
    except FileNotFoundError:
        logging.error(f"Prompt file not found at {prompt_location}")
        prompt = ""

    if token:
        # run the actual bot
        client = bot.get_cli_with_cogs(token=token, prompt=prompt)
        client.run(client.token)
