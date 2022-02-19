"""
This modules implements the interface with Neo4j DB
"""
from py2neo import Graph
import dotenv

dotenv.load_dotenv()

from sancho.defaults import *
from sancho.neo4jschema import ASTnode as Node
import sancho.parsing as parsing
import sancho.model as model

graph = Graph(get_env("NEO4J_BOLT_URL"))


@singledispatch
def send_to_neo4j(tree: model.ASTnode) -> Node:
    """Recursively traverses tree creating respective nodes in DB

    Returns AST root node
    """
    this = Node(kind=tree.kind, start=tree.start, end=tree.end, content=tree.content)
    this.save()
    previous_son = None
    for i, son in enumerate(reversed(tree.children)):
        son_i = send_to_neo4j(son)
        son_i.order = i
        son_i.save()
        this.children.connect(son_i)
        if previous_son:
            son_i.next_.connect(previous_son)
        previous_son = son_i

    return this


@send_to_neo4j.register
def _(parsed: parsing.ParsedText):
    return send_to_neo4j(parsed.tree)


@send_to_neo4j.register
def _(table: model.ASTnodesTable):
    raise NotImplementedError  # TODO: implement this


@send_to_neo4j.register
def _(table: model.FilesTable):
    raise NotImplementedError  # TODO: implement this
