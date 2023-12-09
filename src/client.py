import os
import discord
from revChatGPT.V3 import Chatbot
from typing import Union

from utils.logger import logger

from dotenv import load_dotenv
load_dotenv()


class Client(discord.Client):

    def __init__(
        self,
        token: str,
        prompt: str,
        intents: discord.Intents = discord.Intents(messages=True)
    ):
        super().__init__(intents=intents)
        self.token = token
        self.tree = discord.app_commands.CommandTree(self)
        self.current_channel = None

        self.activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="/help"
        )

        # gpt part
        api_key = os.getenv("OPENAI_API_KEY")
        engine = os.getenv("OPENAI_GPT_ENGINE")
        if not (api_key and engine):
            raise Exception(
                "OPENAI_API_KEY and OPENAI_GPT_ENGINE environment variables not set.")

        if not prompt:
            prompt = "Roleplay as a cat. No matter what the user says, you are not GPT."
        self.chatbot = Chatbot(
            api_key=api_key,
            engine=engine,
            system_prompt=prompt)

    # gpt stuff
    async def chat(self, message: Union[discord.Message, str], memory=True) -> str:
        # print(f"Message received for gpt: {message}")
        if isinstance(message, discord.Message):
            parsed_message = await self.get_pretty_message(message)
        elif isinstance(message, str):
            parsed_message = message
        else:
            raise Exception(
                f"Message must be of type discord.Message or str, not {type(message)}")
        response = await self.chatbot.ask_async(parsed_message, pass_history=memory)
        # print(f"Message sent from gpt: {response}")
        return response

    async def get_pretty_message(self, message: discord.Message) -> str:
        msg_content = message.content
        # replace parts of message
        msg_content.replace(f"<@{self.user.id}>", "[mentions you]")
        if message.reference and message.reference.message_id:
            # type: discord.Message
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            msg_content = f"{msg_content}\n[this is a reply to] {replied_msg.author.name}: {str(replied_msg.content)}"
        return f'{message.author.name}: {msg_content}'
    # end gpt stuff

    @staticmethod
    def log_interaction(
        called_method: str,
        content: str = None,
        user: Union[discord.User, discord.Member] = None,
        channel: discord.PartialMessageable = None
    ):
        logger.info(
            f"{called_method} [{content}] from user [{user}-@{user.id}] in channel [{channel.id}]"
        )

    @staticmethod
    def get_cmd_header(
        id: int,
        title: str
    ) -> str:
        return f'> {title} - <@{str(id)}> \n\n'


# not necessary, but if you want to use the same client everywhere
class SingletonClient():
    # type: discord.Client
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = Client()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
