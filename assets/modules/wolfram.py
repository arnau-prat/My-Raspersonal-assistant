#!/usr/bin/python
# -*- coding: utf-8 -*-

import wolframalpha

class Wolfram:

    def __init__(self):
        self.wolframID = '4X2W9X-AGA34L6QWQ'
    
    def think(self, text):
        client = wolframalpha.Client(self.wolframID)
        res = client.query(text)
        if len(res.pods) > 0:
            texts = ""
            pod = res.pods[1]
            return pod.text       
        else:
            return "I have no answer for that"
