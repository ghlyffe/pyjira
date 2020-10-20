class Search(object):
	def __init__(self, session):
		self.__session = session
		self.__base_url = session.get_url("api/latest/search")

	def search(self,query,params,mode="post"):
		if mode=="post":
			return self.__search_post(query,params)
		elif mode=="get":
			return self.__search_get(query,params)
		else:
			raise Exception("Invalid mode to search: must bet get or post")

	def __search_post(self,query,params):
		params["jql"] = query
		resp = self.__session.post(self.__base_url,json=params)

		if resp.status_code == 200:
			return resp.json()['issues']
		else:
			raise Exception("Error running query, code %d"%resp.status_code)

	def __search_get(self,query,params):
		raise NotImplementedError("No GET method for search")
