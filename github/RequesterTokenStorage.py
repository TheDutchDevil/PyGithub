'''
A class used to manage access to a collection of tokens. Can be used to most
efficiently utilize a set of tokens that are available for setting scraping
jobs 
'''

import threading
import random


class RequesterTokenStorage:

    __tokens = []

    def __init__(self, token_list, rate_limit_resolution_function):
        if len(token_list) == 0:
            raise ValueError("Token list requires at least 1 token")

        for token in token_list:
            self.__tokens.append({
                "token": token,
                "limit": 5000,
                "lock": threading.Lock()
            })

        print(self.__tokens)

            # Ideally we want to check the rate limit of all tokens provided
            # to us

    def get_token(self):
        '''
        Function that returns a token with enough requests left
        '''

        token_ready = None

        # We will check the entire list 3 times
        max_scans = 3
        current_scans = 0

        # Attempt to acquire a token from the list of tokens
        while current_scans <= max_scans and token_ready is None:
            for token in sorted(self.__tokens,key=lambda _: random.random()):
                if token["limit"] > 30:
                    if token["lock"].acquire(blocking=False):
                        token_ready = token
                        break

            current_scans += 1

        if token_ready is None:
            print("Unable to acquire a token")

        return token_ready
