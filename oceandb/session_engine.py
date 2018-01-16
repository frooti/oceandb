import logging

from django.contrib.sessions.backends.base import (CreateError, SessionBase, UpdateError,)
# from django.core.exceptions import SuspiciousOperation
# from django.db import DatabaseError, IntegrityError, router, transaction
# from django.utils import timezone
# from django.utils.encoding import force_text
from django.utils.functional import cached_property

from mongoengine import *
from datetime import datetime, timedelta
db = connect('ocean', host='mongodb://localhost:27017/ocean', username='ocean', password='@cean99')
db["ocean"].authenticate("ocean", password="@cean99")

class Session(Document):
	email = StringField(db_field='e', max_length=150)
	session_key = StringField(db_field='sid', max_length=50, required=True, primary_key=True)
	session_data = StringField(db_field='sdata', max_length=500, required=True)
	expire_date = DateTimeField(db_field='ct', default=None)
	meta = {
		'indexes': [
			('session_key', '-expire_date'),
		]
	}

class SessionStore(SessionBase):
	"""
	Implements database session store.
	"""
	def __init__(self, session_key=None):
		super(SessionStore, self).__init__(session_key)

	@classmethod
	def get_model_class(cls):
		return Session

	@cached_property
	def model(self):
		return self.get_model_class()

	def load(self):
		try:
			s = self.model.objects(session_key=self.session_key, expire_date__gt=datetime.now()).first()
			return self.decode(s.session_data)
		except Exception as e:
			self._session_key = None
			return {}

	def exists(self, session_key):
		if self.model.objects(session_key=session_key).first():
			return True
		else:
			return False

	def create(self):
		while True:
			self._session_key = self._get_new_session_key()
			try:
				# Save immediately to ensure we have a unique entry in the
				# database.
				self.save(must_create=True)
			except CreateError:
				# Key wasn't unique. Try again.
				continue
			self.modified = True
			return

	def create_model_instance(self, data):
		"""
		Return a new instance of the session model object, which represents the
		current session state. Intended to be used for saving the session data
		to the database.
		"""
		return self.model(
			session_key=self._get_or_create_session_key(),
			session_data=self.encode(data),
			expire_date=self.get_expiry_date(),
		)

	def save(self, must_create=False):
		"""
		Saves the current session data to the database. If 'must_create' is
		True, a database error will be raised if the saving operation doesn't
		create a *new* entry (as opposed to possibly updating an existing
		entry).
		"""
		if self.session_key is None:
			return self.create()
		data = self._get_session(no_load=must_create)
		obj = self.create_model_instance(data)
		obj.email = self.get('_auth_user_id')

		try:
			obj.save()
		except:
			raise

	def delete(self, session_key=None):
		if session_key is None:
			if self.session_key is None:
				return
			session_key = self.session_key
		try:
			self.model.objects(session_key=session_key).delete()
		except:
			pass

	@classmethod
	def clear_expired(cls):
		cls.get_model_class().objects(expire_date__lt=datetime.now()).delete()

