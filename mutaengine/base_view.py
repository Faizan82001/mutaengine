from rest_framework import views, status, exceptions
from mutaengine.utils import custom_response


class BaseAPIView(views.APIView):
    def handle_request(self, request, action, *args, **kwargs):
        try:
            response = action(request, *args, **kwargs)
            return response
        except exceptions.AuthenticationFailed as auth_error:
            return custom_response(
                message="Authentication Failed",
                data={"error": str(auth_error)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except exceptions.NotFound as not_found_error:
            return custom_response(
                message="Not Found",
                data={"error": str(not_found_error)},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except exceptions.PermissionDenied as permission_error:
            return custom_response(
                message="Permission Denied",
                data={"error": str(permission_error)},
                status_code=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return custom_response(
                message="Something went wrong!",
                data={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
