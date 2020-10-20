import importlib
import os
import os.path

class ApiLoader(object):
	def __init__(self):
		self.__modules = {}
		self.__path = os.path.abspath(os.path.dirname(__file__))

	def __load_all(self):
		self.__modules = {"api."+i[:-3]:importlib.import_module(".api."+i[:-3],__package__) for i in os.listdir(os.path.sep.join([self.__path,"api"])) if i[-3:] == ".py" and i[:2]!="__"}
		self.__modules.update({"auth."+i[:-3]:importlib.import_module(".auth."+i[:-3],__package__) for i in os.listdir(os.path.sep.join([self.__path,"auth"])) if i[-3:] == ".py" and i[:2]!="__"})
