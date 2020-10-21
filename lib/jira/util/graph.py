import graphviz
from ..api.search import Search

"""
Build a graph of issues that have dependency links.
For any given key, will follow all "blocking" and
"blocked by" links recursively to produce a complete
graph.
"""
class Graph(object):
    def __init__(self, issue):
        """
        Use the JIRA api/issue class to cache all found issues
        """
        self.__issue_cache = issue
        self.__digraph = graphviz.Digraph(format="svg")

    def build_issue_graph(self, key, seen=[]):
        """
        Use the cross-links field of the issue (which we add when we call spider_issue) to build the complete graph
        """
        if key in seen:
            return
        iss = self.__issue_cache.spider_issue(key)
        self.__digraph.node(key)
        seen.append(key)
        # blocked_by
        for k in iss['cross_links']['blocked_by']:
            self.build_issue_graph(k,seen)
            self.__digraph.edge(k,key,label="blocks")
        # blocks
        for k in iss['cross_links']['blocks']:
            self.build_issue_graph(k,seen)
            self.__digraph.edge(key,k,label="blocks")
        # parent_of
        for k in iss['cross_links']['parent_of']:
            self.build_issue_graph(k,seen)
            self.__digraph.edge(key,k,label="parent of")
        # child_of
        for k in iss['cross_links']['child_of']:
            self.build_issue_graph(k,seen)
            self.__digraph.edge(k,key,label="parent of")
        # contains
        for k in iss['cross_links']['contains']:
            self.build_issue_graph(k,seen)
            self.__digraph.edge(key,k,label="epic contains")
        # contained_in_epic
        for k in iss['cross_links']['contained_in_epic']:
            self.build_issue_graph(k,seen)
            self.__digraph.edge(k,key,label="epic contains")

    def render(self,fname="graph"):
        self.__digraph.render(fname)