"""This module uses tree_sitter package to parse files building an AST.


This module exposes:
 - functions:
     get_native_ast
"""
import tree_sitter
from sancho.model import ASTnode, ParsedText


def _get_python_parser() -> tree_sitter.Parser:
    py_language = tree_sitter.Language(
        "resources/compiled/python/languages.so", "python"
    )
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
    return ParsedText(sitter_tree=tree, text=text, path=path)


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

    assert parsed.sitter_tree and parsed.text, "We need sitter_tree and text!"
    ast_tree = _process_node(parsed.sitter_tree.root_node, parsed.text)
    return parsed._replace(tree=ast_tree, sitter_tree=None)


### Test ###
def test_get_native_ast():
    import os

    print(os.getcwd())
    parsed = get_native_ast("sancho/parsing.py")
