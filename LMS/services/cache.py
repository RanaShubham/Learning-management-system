import redis
from decouple import config


class Cache:
    """
    Instantiates cache object and returns same instance for further operations using getInstance()
    """

    __shared_instance = None

    @staticmethod
    def getInstance():
        """[returns initialised cache instance to calling view]
        :return: cache instance stored in __shared_instance
        """

        if Cache.__shared_instance == None:
            Cache.__shared_instance = Cache('localhost',6379)
        return Cache.__shared_instance

    def __init__(self,host,port):
        """[initializes a cache instance with host and port]

        :param host: host to be set for redis
        :param port: port number to be set for redis
        """

        self.cache = redis.StrictRedis(host=host,port=port)

    def set(self,key,value):
        """[sets new key value pair in cache]

        :param key: [mandatory]:[string]:the key to be used for token/note record
        :param value: [mandatory]:[string]:the value to be used for token/note record
        :return: -
        """
        self.cache.set(key,value)
        self.cache.expire(key,time=60*60*5)

    def get(self,key):
        """[gets value for existing key in cache]

        :param key: [mandatory]:[string]:the key to be used for existing token/note record
        :return: value stored against key
        """
        return  self.cache.get(key)

    def delete(self,key):
        """[deletes cache record for existing key in cache]

        :param key: [mandatory]:[string]:the key to be used for existing token/note record
        :return: -
        """
        self.cache.delete(key)











