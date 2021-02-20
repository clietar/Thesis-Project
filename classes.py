class Memo:
    def __init__(self, mem_size):
        self._mem_size = mem_size
        self._index = 0
        self._memo = [None] * mem_size
        self._is_ready = False

    def put(self, x):
        self._memo[self._index] = x
        self._index = (self._index + 1) % self._mem_size
        if self._index == 0:
            self._is_ready = True

    def get(self):
        values = []
        for offset in range(0, self._mem_size):
            values.append(self._memo[(self._index + offset) % self._mem_size])
        return values

    def is_ready(self):
        return self._is_ready