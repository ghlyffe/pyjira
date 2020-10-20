import graphviz
from ..api.search import Search

"""
Build a graph of issues that have dependency links.
For any given key, will follow all "blocking" and
"blocked by" links recursively to produce a complete
graph.
"""
class Graph(object):
    def __init__(self, issue, session = None):
        """
        Use the JIRA api/issue class to cache all found issues
        """
        self.__issue_cache = issue
        self.__session  = session

    def build_issue_graph(self, key, seen=[], links=[]):
        """
        Recursion point for node discovery
        Read the data out of the first issue,
        and use the blocking/blocked-by relations
        to recurse to further issues
        """
        if key in seen:
            return
        seen.append(key)
        issue_resp = self.__issue_cache.get_issue(key)
        blocked_by = [i for i in issue_resp['fields']['issuelinks'] if i['type']['inward'] == "is blocked by"]
        blocks = [i for i in issue_resp['fields']['issuelinks'] if i['type']['inward'] == "blocks"]
        for i in blocks:
            k = i["outwardIssue"]["key"]
            self.build_issue_graph(k, seen, links)
            links.append((key,k,"blocks"))

        for i in blocked_by:
            k = i["inwardIssue"]["key"]
            self.build_issue_graph(k, seen, links)
            links.append((k,key,"blocks"))

        parent_of = [i for i in issue_resp['fields']['issuelinks'] if i['type']['inward'] == 'is child of']
        child_of = [i for i in issue_resp['fields']['issuelinks'] if i['type']['inward'] == 'is parent of']

        for i in child_of:
            k = i["outwardIssue"]["key"]
            self.build_issue_graph(k, seen, links)
            links.append((key,k,"parent of"))

        for i in parent_of:
            k = i["inwardIssue"]["key"]
            self.build_issue_graph(k,seen, links)
            links.append((k,key,"parent of"))

        if 'customfield_10005' in issue_resp.keys() and len(issue_resp['customfield_10005'])>0:
            k = issue_resp['customfield_10005']
            self.build_issue_graph(k, seen, links)
            links.append((k,key,"contains"))

        if self.__session and issue_resp['fields']['issuetype']['name'] == "Epic")
            s = Search()
            in_epic = s.search('"Epic Link" in (%s)'%(key),{"fields":["summary"]})
            for i in in_epic:
                k = i['key']
                self.build_issue_graph(k,seen,links)
                links.append((key,k,"contains"))

        return links
