from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Разрешает доступ к view только пользователям с указанными ролями."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied('У вас нет доступа к этой странице.')
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
