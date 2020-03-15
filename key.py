import random
from Crypto import Random

class Key:
    def __init__(self, length: int):
        super().__init__()
        self._length = length
        self.key = None

    def generate(self):
        """
        generate random key 
        """
        rndfile = Random.new()
        self.key = rndfile.read(self._length)

    def save_txt(self, path: str = 'output/key.txt'):
        """
        save generated key to file
        """
        with open(path, 'w') as file:
            file.write(str(self.key))
