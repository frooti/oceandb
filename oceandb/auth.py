from __future__ import unicode_literals

from mongoengine import *
from datetime import datetime, timedelta
connect('ocean')

class User(Document):
	email = StringField(db_field='e', max_length=150, required=True, primary_key=True)
	password = StringField(db_field='p', max_length=100)
	first_name = StringField(db_field='fn', max_length=100)
	last_name = StringField(db_field='ln', max_length=100)
	is_staff = BooleanField(db_field='is', default=False)
	is_active = BooleanField(db_field='ia', default=True)
	is_superuser = BooleanField(db_field='isu', default=False)
	date_joined = DateTimeField(db_field='dj', default=datetime.now())

	def get_full_name(self):
		"""
		Returns the first_name plus the last_name, with a space in between.
		"""
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

class AnonymousUser(object):
	email = ''
	is_staff = False
	is_active = False
	is_superuser = False

	def __init__(self):
		pass

	def __str__(self):
		return 'AnonymousUser'

	def __eq__(self, other):
		return isinstance(other, self.__class__)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return 1  # instances always return the same hash value

	def save(self):
		raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

	def delete(self):
		raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

	def set_password(self, raw_password):
		raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

	def check_password(self, raw_password):
		raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

	@property
	def is_anonymous(self):
		return CallableTrue

	@property
	def is_authenticated(self):
		return CallableFalse

	def get_username(self):
		return self.username

class ModelBackend(object):
	"""
	Authenticates against settings.AUTH_USER_MODEL.
	"""

	def authenticate(self, request, username=None, password=None, **kwargs):
		if username is None:
			username = kwargs.get('email')
		try:
			user = User.objects(email=username).first()
		except:
			# Run the default password hasher once to reduce the timing
			# difference between an existing and a non-existing user (#20760).
			User().set_password(password)
		else:
			if user.check_password(password) and self.user_can_authenticate(user):
				return user

	def user_can_authenticate(self, user):
		"""
		Reject users with is_active=False. Custom user models that don't have
		that attribute are allowed.
		"""
		is_active = getattr(user, 'is_active', None)
		return is_active or is_active is None

	def get_user(self, user_id):
		try:
			user = User.objects(email=user_id).first()
		except:
			return None
		return user if self.user_can_authenticate(user) else None

class AllowAllUsersModelBackend(ModelBackend):
	def user_can_authenticate(self, user):
		return True
