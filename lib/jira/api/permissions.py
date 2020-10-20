class MyPermissions(object):
	def __init__(self, session, project_key, project_id, issue_key, issue_id):
		self.__session = session
		self.__fullkey = (project_key, project_id, issue_key, issue_id)

		self.__cache = None

	def get_permissions(self, force=False):
		if self.__cache and not force:
			return self.__cache

		resp = session.get
