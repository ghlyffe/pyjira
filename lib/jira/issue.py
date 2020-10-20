from copy import copy
import re

class Issue(object):
    def __init__(self,json):
        self.__key = json['key']
        self.__blocks = [i['outwardIssue']['key'] for i in json['fields']['issuelinks'] if 'outwardIssue' in i.keys()]
        self.__blocked_by = [i['inwardIssue']['key'] for i in json['fields']['issuelinks'] if 'inwardIssue' in i.keys()]
        self.__summary = json['fields']['summary']

        self.__sprint = None
        if 'customfield_10004' in json['fields'] and json['fields']['customfield_10004']:
            m = re.search("name=.*,start",json['fields']['customfield_10004'][0])
            if m:
                self.__sprint = json['fields']['customfield_10004'][0][m.start()+len("name="):m.end()-len(",start")]

        self.__points = 0
        if 'customfield_10002' in json['fields']:
            try:
                self.__points = int(json['fields']['customfield_10002'])
            except TypeError:
                pass
            except ValueError:
                pass

    def blocks(self):
        return copy(self.__blocks)

    def blocked_by(self):
        return copy(self.__blocked_by)

    def node_name(self):
        s = self.__key + ", " + str(self.__sprint) + "[" + str(self.__points) + "]" + "\n" + str(self.__summary)
        return s.replace(':','')

    def __str__(self):
        return self.__key + ": " + self.__summary
