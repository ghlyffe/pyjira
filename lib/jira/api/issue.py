from search import Search

class Issue(object):
    def __init__(self, session):
        self.__session = session
        self.__base_url = session.get_url("api/latest/issue")

        self.__cache = {}

    def get_issue(self, key, fields=None, expand=[], properties = [], updateHistory = False, force = False):
        if key in self.__cache and not force:
            return self.__cache[key]

        params = {}
        if fields:
            params['fields'] = fields
        if expand:
            params['expand'] = expand
        if properties:
            params['properties'] = properties

        resp = self.__session.get(self.__base_url + "/" + key, params=params)
        if resp.status_code == 200:
            self.__cache[key] = resp.json()
        elif resp.status_code == 404:
            raise Exception("Issue not found, or user lacks permissions")
        else:
            raise Exception("Get Issue error code %d"%resp.status_code)
        return self.__cache[key]

    def spider_issue(self, key, fields=None, expand=[], properties=[], updateHistory = False):
        cross_links = {}
        iss = None
        if not key in self.__cache:
            iss = self.get_issue(key, fields, expand, properties, updateHistory, False)

        if not iss:
            return

        if "cross_links" in iss.keys():
            return #We already built cross-links

        cross_links["blocked_by"] = [i for i in iss['fields']['issuelinks'] if i['type']['inward'] == "is blocked by"]
        cross_links["blocks"] = [i for i in iss['fields']['issuelinks'] if i['type']['inward'] == "blocks"]
        cross_links["parent_of"] = [i for i in issue_resp['fields']['issuelinks'] if i['type']['inward'] == 'is child of']
        cross_links["child of"] = [i for i in issue_resp['fields']['issuelinks'] if i['type']['inward'] == 'is parent of']

        cross_links["contained_in_epic"] = []
        if 'customfield_10005' in iss.keys() and len(issue_resp['customfield_10005'])>0:
            cross_links["contained_in_epic"] = iss['customfield_10005']

        cross_links["contains"] = []

        if issue_resp['fields']['issuetype']['name'] == "Epic")
            s = Search(self.__session)
            in_epic = s.search('"Epic Link" in (%s)'%(key),{"fields":["summary"]})
            cross_links["contains"].extend([i['key'] for i in in_epic])



        iss["cross_links"] = cross_links

        keylist = []
        keylist.extend(cross_links["blocked_by"])
        keylist.extend(cross_links["blocks"])
        keylist.extend(cross_links["parent_of"])
        keylist.extend(cross_links["child_of"])
        keylist.extend(cross_links["contained_in_epic"])
        keylist = set(keylist) - set(self.__cache.keys())

        for k in keylist:
            self.spider_issue(k,fields,expand,properties,updateHistory)