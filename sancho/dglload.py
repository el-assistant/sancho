"""
This module implents data loading into DGL library
"""
from defaults import *

import dgl
import torch as th
from parsing import ParsedText
from neo4jschema import ASTnode as N4node


def get_coo(node: N4Node):
    assert node.kind == "module"
    visited = {}
    # TODO: tag nodes by file name to improve query


def make_dgl_graph(parsed: ParsedText) -> dgl.DGLGraph:
    assert parsed.tree
    pass
