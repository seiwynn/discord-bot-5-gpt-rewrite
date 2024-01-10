import asyncio
import multiprocessing

import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import client, get_bots


def start_bot_process(bot: client.Client, queue: multiprocessing.Queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def bot_task():
        await bot.start(bot.token)

    async def check_queue():
        print(f"Starting bot {bot.id} and checking queue.")
        while True:
            if not queue.empty():
                message = queue.get()
                # Assuming each bot has a unique id attribute
                if message == f"SHUTDOWN_{bot.id}":
                    print(f"Shutting down bot {bot.id}.")
                    await bot.close()
                    break
            # Sleep for a bit before checking the queue again
            await asyncio.sleep(1)

    loop.run_until_complete(asyncio.gather(bot_task(), check_queue()))
    loop.close()


class BotManager:
    def __init__(self, bots):
        self.bots = bots
        self.processes = [None for _ in range(len(bots))]
        self.queue = multiprocessing.Queue()

    def start_bot(self, index):
        bot = self.bots[index]
        if self.processes[index] is not None:
            return
        p = multiprocessing.Process(
            target=start_bot_process, args=(bot, self.queue))
        p.start()
        self.processes[index] = p

    def stop_bot(self, index):
        bot = self.bots[index]
        # Send shutdown message to the queue
        self.queue.put(f"SHUTDOWN_{bot.id}")
        self._kill_process(index)  # Then terminate the process

    def _kill_process(self, index):
        process = self.processes[index]
        process.terminate()
        self.processes[index] = None

    def start_all(self):
        for i in range(len(self.bots)):
            self.start_bot(i)

    def stop_all(self):
        for i in range(len(self.bots)):
            self.stop_bot(i)


if __name__ == "__main__":
    bots = get_bots.get_bots()  # Get a list of bots
    manager = BotManager(bots)
    manager.start_all()

