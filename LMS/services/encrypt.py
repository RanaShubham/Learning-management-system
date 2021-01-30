import jwt
from decouple import config


class Encrypt:
    """[contains methods for encoding token with id,role and time and decoding existing token]

    Returns:
        [encode or decode result]: [token or payload]
    """

    @staticmethod
    def decode(token):
        return jwt.decode(token, config('ENCODE_SECRET_KEY'), algorithms=["HS256"])

    @staticmethod
    def encode(user_id,role, current_time):
        return jwt.encode({"id": user_id, "role":role ,"current_time": current_time}, config('ENCODE_SECRET_KEY'), algorithm="HS256")

    @staticmethod
    def encode_reset(user_id, current_time):
        return jwt.encode({"id": user_id, "current_time": current_time}, config('ENCODE_SECRET_KEY'), algorithm="HS256")
