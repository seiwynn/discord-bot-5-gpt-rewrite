import asyncio
import multiprocessing
from src import client

def start_bot_process(bot: client.Client, queue: multiprocessing.Queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def bot_task():
        await bot.start(bot.token)
    
    async def check_queue():
        while True:
            if not queue.empty():
                message = queue.get()
                if message == f"SHUTDOWN_{bot.id}":  # Assuming each bot has a unique id attribute
                    print(f"Shutting down bot {bot.id}.")
                    await bot.close()
                    break
            await asyncio.sleep(1)  # Sleep for a bit before checking the queue again

    loop.run_until_complete(asyncio.gather(bot_task(), check_queue()))
    loop.close()

class BotManager:
    def __init__(self, bots):
        self.bots = bots
        self.processes = [None for _ in range(len(bots))]
        self.queue = multiprocessing.Queue()

    def start_bot(self, index):
        bot = self.bots[index]
        p = multiprocessing.Process(target=start_bot_process, args=(bot))
        p.start()
        self.processes[index] = p

    def stop_bot(self, index):
        bot = self.bots[index]
        self.queue.put(f"SHUTDOWN_{bot.id}")  # Send shutdown message to the queue
        self._kill_bot_process(index)  # Then terminate the process

    def _kill_bot_process(self, index):
        process = self.processes[index]
        process.terminate()
        self.processes[index] = None

    def start_all(self):
        for i in range(len(self.bots)):
            self.start_bot(i)

    def stop_all(self):
        for i in range(len(self.bots)):
            self.stop_bot(i)

# # Example usage
# bot1 = Client()
# bot2 = Client()
# bot3 = Client()
# manager = BotManager([bot1, bot2, bot3])

# # Start a specific bot
# manager.start_bot(0)

# # Stop a specific bot gracefully
# asyncio.run(manager.stop_bot(0))

# # Start all bots
# manager.start_all()

# # Stop all bots
# manager.stop_all()
