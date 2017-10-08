from django.conf import settings
from django.utils.crypto import constant_time_compare
from auth import User, AnonymousUser

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'

def get_user(request):
    if not hasattr(request, '_cached_user'):
    	user = None
    	try:
	        email = request.session[SESSION_KEY]
	        backend_path = request.session[BACKEND_SESSION_KEY]
	    except KeyError:
	        pass
	    else:
	        if backend_path in settings.AUTHENTICATION_BACKENDS:
	            backend = load_backend(backend_path)
	            user = backend.get_user(email)
	            # Verify the session
	            if hasattr(user, 'get_session_auth_hash'):
	                session_hash = request.session.get(HASH_SESSION_KEY)
	                session_hash_verified = session_hash and constant_time_compare(
	                    session_hash,
	                    user.get_session_auth_hash()
	                )
	                if not session_hash_verified:
	                    request.session.flush()
	                    user = None

	   	request._cached_user = user
    return request._cached_user

class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        request.user = SimpleLazyObject(lambda: get_user(request))