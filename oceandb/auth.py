from __future__ import unicode_literals
from django.utils.crypto import get_random_string, salted_hmac
from django.contrib.auth.hashers import make_password
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

	def create_user(self, email, password, **extra_fields):
		"""
		Creates and saves a User with the given username, email and password.
		"""
		if not username:
			raise ValueError('The given username must be set')
		email = self.normalize_email(email)
		user = User(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user

	@classmethod
	def normalize_email(cls, email):
		"""
		Normalize the email address by lowercasing the domain part of it.
		"""
		email = email or ''
		try:
			email_name, domain_part = email.strip().rsplit('@', 1)
		except ValueError:
			pass
		else:
			email = '@'.join([email_name, domain_part.lower()])
		return email

	def set_password(self, raw_password):
		self.password = make_password(raw_password)
		self._password = raw_password

	def check_password(self, raw_password):
		"""
		Return a boolean of whether the raw_password was correct. Handles
		hashing formats behind the scenes.
		"""
		def setter(raw_password):
			self.set_password(raw_password)
			# Password hash upgrades shouldn't be considered password changes.
			self._password = None
			self.save(update_fields=["password"])
		return check_password(raw_password, self.password, setter)

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
