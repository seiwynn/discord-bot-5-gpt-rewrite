# currently not in use
import itertools

class RoundRobinAPIKeys:
    def __init__(self, keys):
        self.keys = keys
        self.key_iterator = itertools.cycle(self.keys)

    def get_next_key(self):
        return next(self.key_iterator)

# Example Usage
api_keys = ["key1", "key2", "key3", "key4"]
key_manager = RoundRobinAPIKeys(api_keys)

for _ in range(10):  # Example of making 10 API calls
    key = key_manager.get_next_key()
    print(f"Using API Key: {key}")
    # Add your API call logic here using the 'key'
