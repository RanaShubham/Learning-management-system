import enum
from rest_framework import status

class ExceptionType(enum.Enum):
    UserException = "Cannot create user instance."
    NonExistentError = "Requested user does not exist"
    UnauthorizedError = "Sorry, you are not authorized to perform this operation."
    StudentNotFound = "student data not found"
    StudentExist = "student already exist"
    MentorExists = "mentor already exists"
    PerformanceRecordExists = "Performance record of the student for this course already exiits."
    

class LMSException(Exception):
    """[Custom exception.]
    Args:
        Exception (Enum)): [Exception type indicated by enum]
        Exception (str): [Message showing details of error.]
    """

    def __init__(self, *args):
        self.exception_type = args[0]
        self.message = args[1]
        self.status_code = args[2]

    def __str__(self):
        return self.message

def admin_only(func):
    def wrapper(*args, **kwargs):
        if kwargs.get('role') != 'admin':
            raise LMSException(ExceptionType.UnauthorizedError, "Only admin access allowed", status.HTTP_401_UNAUTHORIZED)
        return func(*args, **kwargs)
    
    return wrapper