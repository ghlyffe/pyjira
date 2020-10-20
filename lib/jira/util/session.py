import re
import requests


class Session(requests.Session):
	def __init__(self, base_url):
		requests.Session.__init__(self)
		self.stream = True
		self.__base_url = base_url
		
	def get_url(self, url):
		tmp = '/'.join([self.__base_url, url])
#		return re.sub('/+','/',tmp)
		return tmp

