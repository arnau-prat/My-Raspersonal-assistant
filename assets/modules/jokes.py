#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
class Jokes:

    def __init__(self, path):
        self.path = path
        self.name = 'jokes.txt'

    def think(self):
        jokeFile = open(self.path + self.name, "r")
        jokes = []
        for line in jokeFile.readlines():
            jokes.append(line)
        return random.choice(jokes)

if __name__ == '__main__':
    # Jokes Test
    joke = Jokes("./")
    print joke.think()

    