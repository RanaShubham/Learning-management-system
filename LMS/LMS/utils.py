import enum

class ExceptionType(enum.Enum):
    UserException = "Cannot create user instance."
    NonExistentError = "Requested user does not exist"
    UnauthorizedError = "Sorry,you are not authorized to perform this operation."
    RoleError = "No such role exists."

class LMSException(Exception):
    """[Custom exception.]
    Args:
        Exception (Enum)): [Exception type indicated by enum]
        Exception (str): [Message showing details of error.]
    """
    def __init__(self, *args):
    
        self.exception_type = args[0]
        self.message = args[1]
             
    def __str__(self):
        return self.message