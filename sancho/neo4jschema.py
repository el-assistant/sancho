"""
This module describes the schema implemented in Neo4j using neomodel python package.

The following bash command is used to migrate the model:
neomodel_install_labels [path-to-this-file]

Otherwise, one can use install_all_labels from neomodel
"""

import os

import neomodel as nm

import dotenv

dotenv.load_dotenv()

from sancho.defaults import get_env

nm.config.DATABASE_URL = get_env("NEO4J_BOLT_URL")


class ASTnode(nm.StructuredNode):
    """Defines schema for an AST node in Neo4j db.

    This ASTnode model differs from the one defined in parsing.py by the fields
    order and next_. Both fields were added to keep the ordering infromation
    between children nodes of the same parent.
    """

    kind = nm.StringProperty(required=True)
    start = nm.IntegerProperty()
    end = nm.IntegerProperty()
    content = nm.StringProperty()
    order = nm.IntegerProperty()
    children = nm.RelationshipTo("ASTnode", "D")
    next_ = nm.RelationshipTo("ASTnode", "N")


class FileNode(nm.StructuredNode):
    """Defines schema for a file node in Neo4j db."""

    path = nm.RelationshipFrom("DirNode", "D")
    name = nm.StringProperty(required=True)
    ast_root = nm.RelationshipTo("ASTnode", "D")


class DirNode(nm.StructuredNode):
    """Defines schema for a directory node in Neo4j db."""

    path = nm.RelationshipFrom("DirNode", "D")
    name = nm.StringProperty()
    project_root = nm.BooleanProperty()


def migrate():
    nm.install_all_labels()


# TODO: This schema will be useless if we load the data through LOAD CSV command
