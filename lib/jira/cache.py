import requests
import json
import graphviz

from issue import Issue

class JiraCache(object):
    def __init__(self, user, pwd, jira_base="https://jira.etas-dev.com/rest/"):
        self.__cache = {}
        self.__session = requests.Session()
        self.__session.stream = True
        self.__auth = (user,pwd)
        self.__jira_base = jira_base
        self.__cur_user = None

    def jira_auth(self):
        if self.__cur_user:
            return

        resp = self.__session.post(self.__jira_base + "auth/latest/session", json = {'username':self.__auth[0], 'password':self.__auth[1]})

        if(resp.status_code == 200):
            cu = self.__session.get(self.__jira_base + "auth/latest/session")
            if(cu.status_code != 200):
                raise Exception("Error getting user after successful login")
            else:
                self.__cur_user = cu
        else:
            raise Exception("Failed to log in to Jira instance")

    def build_issue_graph(self,key,force=False):
        if not self.__cur_user:
            raise Exception("Cannot build issue graph - not logged in")


        if not force and key in self.__cache:
            return self.__cache[key]

        issue_resp = self.__session.get(self.__jira_base + "api/latest/issue/" + key)
        if issue_resp.status_code == 200:
            pass
        elif issue_resp.status_code == 404:
            raise Exception("Key " + key + " is not recognised")
        elif issue_resp.status_code in (401,403):
            self.__cur_user = None
            raise Exception("User not authenticated or authentication expired")
        else:
            raise Exception("Got unexpected status code " + str(issue_resp.status_code))

        try:
            issue = Issue(issue_resp.json())
            self.__cache[key] = issue
            #uplinks
            for i in issue.blocked_by():
                self.build_issue_graph(i)
            #downlinks
            for i in issue.blocks():
                self.build_issue_graph(i)
        except Exception as e:
            f = open(key + "_err.json","w")
            json.dump(issue_resp.json(), f)
            f.close()
            raise

        return self.__cache[key]


    def render(self):
        dg = graphviz.Digraph(format='svg')
        local_cache = []
        for k in self.__cache:
            if k in local_cache:
                pass
            self.__render_all(dg,local_cache,k)
        dg.render('graph')

    def __render_all(self, dg, cache, key):
        if key in cache:
            return

        dg.node(self.__cache[key].node_name())
        cache.append(key)
        
        for blocks in self.__cache[key].blocks():
            self.__render_all(dg, cache, blocks)
            if (key,blocks) not in cache:
                dg.edge(self.__cache[key].node_name(),self.__cache[blocks].node_name())
                cache.append((key,blocks))

        for blocked_by in self.__cache[key].blocked_by():
            self.__render_all(dg, cache, blocked_by)
            if (blocked_by,key) not in cache:
                dg.edge(self.__cache[blocked_by].node_name(),self.__cache[key].node_name())
                cache.append((blocked_by,key))
