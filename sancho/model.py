"""
Entity modelling for the whole project is described here.
"""


from sancho.defaults import *
import tree_sitter


class Repo(NamedTuple):
    full_name: str


class File(NamedTuple):
    repo: Repo
    full_path: str


class ASTnode(NamedTuple):
    """It is a node and a tree at the same time, since the children nodes are nested
    in a tuple. So the root node is actually the whole tree. Field 'kind' is the
    kind of the node as defined in tree-sitter respective grammar. 'start' and
    'end' are the position of the parsed structure in the source text. 'content'
    has the raw content of the parsed text. It is filled only for some kinds of
    nodes. For example, we track the content of 'identifier' nodes, so that we
    can enrich the AST with symbol references later.

    """

    kind: str
    start: int
    end: int
    children: Tuple["ASTnode"]
    content: str = None


class ParsedText(NamedTuple):
    """
    Contains the AST of a file, together with the source code and some metadata.

    sitter_tree contains the AST in the format provided by tree-sitter package,
    whereas tree contains the AST defined as a NamedTuple. Once tree is defined,
    sitter_tree can be discarded.
    """

    sitter_tree: tree_sitter.Tree = None
    tree: ASTnode = None
    text: bytes = None
    path: str = None
