# Create your views here.

from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from LMS.utils import LMSException, ExceptionType
from account.decorators import user_login_required
from account.models import User, Role
from account.utils import Util
from course.models import Course
from course.serializers import CourseSerializer, CourseGetSerializer
from account.models import User, Role
from django.db.models import Q
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from services.logging import loggers
from performance_info.models import PerformanceInfo
from performance_info.serializers import PerformanceInfoSerializer
from mentor.models import Mentor
from mentor.serializers import MentorSerializer

logger = loggers("log_course.log")


@method_decorator(user_login_required, name='dispatch')
class CourseRegisterView(generics.GenericAPIView):
    """
    Created a class to perform crud operations for the course which is taken by students
    """
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def post(self, request, **kwargs):
        """
        @param request: name : name of the course
                        @type: str
                        price: price of the course
                        @type: float
                        duration: duration of the course
                        @type: str
                        description: brief explanation about the course
                        @type:str
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[pk] : primary key of specific course
        @type: int
        """
        try:
            admin_role = Role.objects.filter(Q(role='admin')).first()
            if admin_role:
                role = admin_role
            else:
                raise LMSException(ExceptionType.UserException, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
            user = User.objects.filter(Q(id=kwargs['userid']), (Q(role=role.role_id))).first()
            if user is None:
                raise LMSException(ExceptionType.UserException, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = Util.manage_response(status=True, message='course details added', data=serializer.data,
                                                log='course details added', logger_obj=logger)
                return Response(response, status.HTTP_201_CREATED)
            raise LMSException(ExceptionType.UserException, 'Please enter valid details', status.HTTP_400_BAD_REQUEST)
        except LMSException as e:
            response = Util.manage_response(status=False, message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code)
        except Exception as e:
            response = Util.manage_response(status=False, message="Something went wrong.",
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)


@api_view()
def retrieve_courses(request, **kwargs):
    try:
        course = Course.objects.filter(is_deleted=False)
        if course is None:
            raise LMSException(ExceptionType.NonExistentError, 'No such course found',
                               status.HTTP_400_BAD_REQUEST)
        serializer = CourseGetSerializer(course, many=True)
        response = Util.manage_response(status=True, message='course details retrieved', data=serializer.data,
                                        log='course details retrieved', logger_obj=logger)
        return Response(response, status.HTTP_200_OK)
    except LMSException as e:
        response = Util.manage_response(status=False,
                                        message=e.message,
                                        log=e.message, logger_obj=logger)

        return Response(response, e.status_code, content_type="application/json")
    except Exception as e:
        response = Util.manage_response(status=False, message=str(e),
                                        log=str(e), logger_obj=logger)
        return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def retrieve_course(request, **kwargs):
    """
          [displays specific course data ]
          args: kwargs[pk]: user id of the user
          Returns:
              Response: status , message and data
              @type: status: Boolean, message:str, data: list
          """
    try:
        course = Course.objects.filter(Q(id=kwargs.get('pk')), Q(is_deleted=False)).first()
        if course is None:
            raise LMSException(ExceptionType.NonExistentError, 'No such course found',
                               status.HTTP_400_BAD_REQUEST)
        serializer = CourseSerializer(course)
        response = Util.manage_response(status=True, message='course details retrieved', data=serializer.data,
                                        log='course details retrieved', logger_obj=logger)
        return Response(response, status.HTTP_200_OK)

    except LMSException as e:
        response = Util.manage_response(status=False,
                                        message=e.message,
                                        log=e.message, logger_obj=logger)

        return Response(response, e.status_code, content_type="application/json")
    except Exception as e:
        response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                        log=str(e), logger_obj=logger)
        return Response(response, status.HTTP_400_BAD_REQUEST)


@method_decorator(user_login_required, name='dispatch')
class CourseView(generics.GenericAPIView):
    """
    Created a class to perform crud operations for the course which is taken by students
    """
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def patch(self, request, **kwargs):
        """

        @param request: name : name of the course
                        @type: str
                        price: price of the course
                        @type: float
                        duration: duration of the course
                        @type: str
                        description: brief explanation about the course
                        @type:str
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[pk] : primary key of specific course
        @type: int
        """
        try:
            admin_role = Role.objects.filter(Q(role='admin')).first()
            if admin_role:
                role = admin_role
            else:
                raise LMSException(ExceptionType.UserException, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
            user = User.objects.filter(Q(id=kwargs['userid']), (Q(role=role.role_id))).first()
            if user is None:
                raise LMSException(ExceptionType.UserException, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
            if kwargs.get('pk'):
                course = Course.objects.get(id=kwargs.get('pk'))
                serializer = CourseSerializer(course, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    response = Util.manage_response(status=True, message='course details updated', data=serializer.data,
                                                    log='course details updated', logger_obj=logger)
                    return Response(response, status.HTTP_200_OK)
                raise LMSException(ExceptionType.UserException, 'Please enter valid details',
                                   status.HTTP_400_BAD_REQUEST)
            raise LMSException(ExceptionType.NonExistentError, 'Please enter the specific course id',
                               status.HTTP_400_BAD_REQUEST)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        """
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[pk] : primary key of specific course
        @type: int
        """
        try:
            admin_role = Role.objects.filter(Q(role='admin')).first()
            if admin_role:
                role = admin_role
            else:
                raise LMSException(ExceptionType.UserException, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
            user = User.objects.filter(Q(id=kwargs['userid']), (Q(role=role.role_id))).first()
            if user is None:
                raise LMSException(ExceptionType.UserException, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
            if kwargs.get('pk'):
                course = Course.objects.get(id=kwargs['pk'])
                if course is None:
                    raise LMSException(ExceptionType.NonExistentError, 'No such course found',
                                       status.HTTP_400_BAD_REQUEST)
                course.soft_delete()
                response = Util.manage_response(status=True,
                                                message='Deleted successfully.',
                                                log='Deleted course successfully.', logger_obj=logger)
                return Response(response, status.HTTP_204_NO_CONTENT)
            raise LMSException(ExceptionType.NonExistentError, 'Please enter the specific course id',
                               status.HTTP_400_BAD_REQUEST)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)


@method_decorator(user_login_required, name='dispatch')
class CoursePerformanceDetails(generics.GenericAPIView):
    """
    Created a class to get all course details by count of students and mentors associated to a course
    """
    def get_serializer_class(self):
        pass

    def get(self, request, **kwargs):
        """
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[role] : role of the logged in person
        @type: string
        """
        try:
            if kwargs['role'] == 'admin':
                courses = Course.objects.all()
                performance = {}
                for item in courses:
                    performance_data = PerformanceInfo.objects.filter(course_id=item.id)
                    mentors = Mentor.objects.filter(course=item.id)
                    sample = PerformanceInfoSerializer(performance_data, many=True)
                    mentors_list = MentorSerializer(mentors, many=True)
                    performance[item.name] = {"mentor_count": mentors_list.data.__len__(),
                                              "student_count": sample.data.__len__()}
                response = Util.manage_response(status=True, message='course details retrieved', data=performance,
                                                log='course details retrieved', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
            else:
                raise LMSException(ExceptionType.UnauthorizedError, 'you are not authorized to perform this operation',
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)
