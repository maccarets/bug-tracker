from django.http import Http404

from bug_tracker.views import handler404


class BaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        pass


class PermissionDeniedMiddleware(BaseMiddleware):
    def process_exception(selr, request, exception):
        if isinstance(exception, Http404):
            return handler404(request, exception)
