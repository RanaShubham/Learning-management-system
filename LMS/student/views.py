from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework import status, generics
from rest_framework.response import Response

from account.serializers import RegisterSerializer
from course.models import Course
from mentor.models import Mentor
from services.logging import loggers
from .serializers import StudentSerializer
from .models import Student
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.models import User, Role
from django.db.models import Q
from LMS.utils import *

from account.utils import Util
from services.logging import loggers
from .models import Student
from .serializers import StudentSerializer

from performance_info.serializers import *

logger = loggers("log_students.log")


@method_decorator(user_login_required, name='dispatch')
class CreateStudent(generics.GenericAPIView):
    """
    Created a class to register a student with user details together
    """

    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def post(self, request, **kwargs):
        """
        A method to post student details
        @param request: name: name of student (mandatory)
                        @type:str
                        phone_number: phone number of student (mandatory)
                        @type:str
                        college: college the student admitted
                        @type:str
                        git_link: git link of the student
                        @type:str

        @return: status, message and status code
        @rtype: status: boolean, message: str
        """
        try:

            current_user_role = kwargs.get('role')
            if current_user_role != 'admin':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
            normalized_admission_role = request.data['role'].lower()
            admission_role_obj = Role.objects.filter(role=normalized_admission_role).first()
            if not admission_role_obj:
                raise LMSException(ExceptionType.RoleError, "{} is not a valid role.".format(normalized_admission_role),
                                   status.HTTP_400_BAD_REQUEST)

            request.POST._mutable = True
            request.data['role'] = admission_role_obj.pk
            request.POST._mutable = False
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            user = User.objects.filter(email=serializer.data['email']).first()
            Util.send_email(user)
            if not user:
                raise LMSException(ExceptionType.NonExistentError, "No such user record found.",
                                   status.HTTP_404_NOT_FOUND)
            if Student.objects.filter(user=user.id).first():
                raise LMSException(ExceptionType.StudentExist, "An account with this user already exists.",

                                   status.HTTP_400_BAD_REQUEST)
            request.POST._mutable = True
            request.data["user"] = user.id
            request.POST._mutable = False
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                student_obj = serializer.save()
            request.POST._mutable = True
            request.data["student_id"] = student_obj.id
            request.POST._mutable = False
            if not Course.objects.filter(id=request.data['course_id']).first():
                raise LMSException(ExceptionType.NonExistentError, "Course does not exist", status.HTTP_404_NOT_FOUND)
            if not Mentor.objects.filter(id=request.data['mentor_id']).first():
                raise LMSException(ExceptionType.NonExistentError, "Course does not exist", status.HTTP_404_NOT_FOUND)
            serializer = PerformanceInfoSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            response = Util.manage_response(status=True,
                                            message='Student details added successfully.', data=serializer.data,
                                            log='Student details added successfully.', logger_obj=logger)
            return Response(response, status=status.HTTP_201_CREATED)

        except Student.DoesNotExist as e:

            response = Util.manage_response(status=False,
                                            message="Requested course does not exist",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")


@method_decorator(user_login_required, name='dispatch')
class StudentsDetails(generics.GenericAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get(self, request, **kwargs):
        """
        [displays specific student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            if kwargs['role'] == 'admin':
                student_list = Student.objects.all()
                serializer = StudentSerializer(student_list, many=True)
                student_data_list = []
                for item in serializer.data:
                    student_details = User.objects.get(id=item['student_id'])
                    data = {'name': student_details.name, 'email': student_details.email,
                            'phone_number': student_details.phone_number}
                    data.update(item)
                    data.pop('user')
                    student_data_list.append(data)
                response = Util.manage_response(status=True, message='student details retrieved',
                                                data=student_data_list,
                                                log='student details retrieved', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except User.DoesNotExist:
            response = Util.manage_response(status=False,
                                            message='The student does not exist',
                                            log='The student does not exist', logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")


@method_decorator(user_login_required, name='dispatch')
class StudentDetails(generics.GenericAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get(self, request, **kwargs):
        """
        [displays specific student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            user = User.objects.get(id=kwargs['userid'])  # requesting user:admin/student
            student_details = Student.objects.filter(Q(student_id=kwargs['pk'])).first()
            if student_details is None:
                raise LMSException(ExceptionType.StudentNotFound, 'No such student found', status.HTTP_400_BAD_REQUEST)
            elif student_details.student_id == user.id or kwargs['role'] == 'admin':
                serializer = StudentSerializer(student_details)
                data = {'name': student_details.user.name, 'email': student_details.user.email,
                        'phone_number': student_details.user.phone_number}
                data.update(serializer.data)
                data.pop('user')
                response = Util.manage_response(status=True, message='student details retrieved',
                                                data=data,
                                                log='student details retrieved', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except User.DoesNotExist:
            response = Util.manage_response(status=False,
                                            message='The student does not exist',
                                            log='The student does not exist', logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def put(self, request, *args, **kwargs):
        """
        [updates the respective student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            if kwargs['role'] == 'student':
                if kwargs['pk'] == kwargs['userid']:
                    user = User.objects.get(id=kwargs['userid'])
                    details = Student.objects.filter(Q(student_id=user.id)).first()
                    if details is None:
                        raise LMSException(ExceptionType.UserException,
                                           "You have not registered your education details.",
                                           status.HTTP_401_UNAUTHORIZED)
                    if details.user_id == kwargs['pk']:
                        data = request.data
                        serializer = StudentSerializer(details, data=data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            data = {'name': user.name, 'email': user.email,
                                    'phone_number': user.phone_number}
                            data.update(serializer.data)
                            data.pop('user')
                            response = Util.manage_response(status=True, message='data updated successfully',
                                                            data=data,
                                                            log='data updated successfully', logger_obj=logger)
                            return Response(response, status.HTTP_200_OK)
                        response = Util.manage_response(status=False,
                                                        message='please enter the valid details',
                                                        log='please enter the valid details', logger_obj=logger)
                        return Response(response, status.HTTP_400_BAD_REQUEST)
                    else:
                        raise LMSException(ExceptionType.UserException,
                                           "Sorry,you are not authorized to perform this operation.",
                                           status.HTTP_401_UNAUTHORIZED)
                else:
                    raise LMSException(ExceptionType.UserException,
                                       "Sorry,you have entered invalid id, please enter your id.",
                                       status.HTTP_401_UNAUTHORIZED)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not student to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except Student.DoesNotExist:
            response = Util.manage_response(status=False,
                                            message='The student does not exist',
                                            log='The student does not exist', logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
