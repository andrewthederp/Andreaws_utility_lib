import random as _random
import time


class Random:
    """Predicting the random outcome... But not really"""
    def __init__(self):
        self.seed = time.time()

        self.random = _random.Random(self.seed)
        self.predict_random = _random.Random(self.seed)

    def peek_random(self):
        r = self.predict_random.random()
        self.predict_random.seed(self.seed)
        return r

    def random(self):
        r = self.random.random()
        self.__init__()
        return r


    def peek_randrange(self, *args, **kwargs):
        r = self.predict_random.randrange(*args, **kwargs)
        self.predict_random.seed(self.seed)
        return r

    def randrange(self, *args, **kwargs):
        r = self.predict_random.randrange(*args, **kwargs)
        self.__init__()
        return r


    def peek_randint(self, *args, **kwargs):
        r = self.predict_random.randint(*args, **kwargs)
        self.predict_random.seed(self.seed)
        return r

    def randint(self, *args, **kwargs):
        r = self.predict_random.randint(*args, **kwargs)
        self.__init__()
        return r


    def peek_choice(self, *args, **kwargs):
        r = self.predict_random.choice(*args, **kwargs)
        self.predict_random.seed(self.seed)
        return r

    def choice(self, *args, **kwargs):
        r = self.predict_random.choice(*args, **kwargs)
        self.__init__()
        return r

