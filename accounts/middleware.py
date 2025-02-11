from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Ensure the user is authenticated first.
            if not request.user.is_authenticated:
                return redirect('login_view')

            if request.user.role in required_role:
                return view_func(request, *args, **kwargs)
            return redirect('sell')
        return _wrapped_view
    return decorator
