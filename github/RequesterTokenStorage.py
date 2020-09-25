import threading
import random
import datetime


class RequesterTokenStorage:
    '''
    A class used to manage access to a collection of tokens. Can be used to most
    efficiently utilize a set of tokens that are available for setting scraping
    jobs 
    '''

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

            # Ideally we want to check the rate limit of all tokens provided
            # to us

    def __update_reset_times(self):
        '''
        Goes through all tokens and attempts to reset their token limits based
        on the raw reset time as returned by GitHub
        '''
        for token in self.__tokens:
            if "reset_time" in token:
                if token["lock"].acquire(blocking=False):
                    try:
                        if datetime.datetime.fromtimestamp(token["reset_time"]) <= datetime.datetime.now():
                            token["limit"] = 5000
                    finally:
                        token["lock"].release()

    def get_token(self):
        '''
        Function that returns a token with enough requests left
        '''

        token_ready = None

        self.__update_reset_times()

        # We will check the entire list 3 times, allowing a wait time of 
        # 200 ms per block
        max_scans = 3
        current_scans = 0

        # Attempt to acquire a token from the list of tokens
        while current_scans <= max_scans and token_ready is None:
            for token in sorted(self.__tokens,key=lambda _: random.random()):
                if token["lock"].acquire(blocking=True, timeout=.2):
                    token_ready = token
                    break

            current_scans += 1

        if token_ready is None:
            print("Unable to acquire a token")

        return token_ready

    def get_max_limit(self):
        # 5000 requests per token is the max limit
        return len(self.__tokens) * 5000
    
    def get_current_limit(self):
        self.__update_reset_times()
        return sum([token["limit"] for token in self.__tokens])
