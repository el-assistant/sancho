"""This module uses tree_sitter package to parse files building an AST.

Coding guidelines:
- Functions first
- Use immutables objects
- Separate data from functions, but still define data structure
- Prefer native python libraries and types

In practical terms, we use NamedTuple instead of dict and tuple instead of list.
Additionally, we use NamedTuple from typing instead of namedtuple from
collections because it allows to define data types through hints, which becomes
very handy for code completion. It also provides the possibility to add
docstrings to the data. Data that leaves a module should always be a NamedTuple,
ideally containing only native data types. Providing a docstring for these named
tuples is very important since the data will carry its methods as in OO
programming.

This module exposes:
 - data:
     ASTnode
     ParsedText
 - functions:
     get_native_ast
"""

from defaults import *
import tree_sitter


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
    language: str = None


def _get_python_parser() -> tree_sitter.Parser:
    py_language = tree_sitter.Language("tree-sitter-languages/languages.so", "python")
    parser = tree_sitter.Parser()
    parser.set_language(py_language)
    return parser


def _filepath_to_string(path, enc):
    with open(path, encoding=enc) as file:
        s = file.read()
    return s


def _parse_python_file(path, enc="utf-8"):
    parser = _get_python_parser()
    text = _filepath_to_string(path, enc)
    text = bytes(text, enc)
    tree = parser.parse(text)
    return ParsedText(sitter_tree=tree, text=text, language="python", path=path)


def _process_node(node: tree_sitter.Node, text: bytes) -> ASTnode:
    def should_track_content(node: tree_sitter.Node) -> bool:
        return node.type == "identifier"

    return ASTnode(
        kind=node.type,
        start=node.start_byte,
        end=node.end_byte,
        children=tuple([_process_node(c, text) for c in node.children]),
        content=text[node.start_byte : node.end_byte]
        if should_track_content(node)
        else None,
    )


def get_native_ast(path: str) -> ParsedText:
    parsed = _parse_python_file(path)
    breakpoint()
    assert parsed.sitter_tree and parsed.text, "We need sitter_tree and text!"
    ast_tree = _process_node(parsed.sitter_tree.root_node, parsed.text)
    return parsed._replace(tree=ast_tree, sitter_tree=None)


"""
test it
"""
parsed = get_native_ast("parsing.py")
