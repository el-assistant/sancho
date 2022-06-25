""" Contains functions to load data into SQL DB
"""
from sancho.defaults import *
from sancho.model import ASTnodesTable, FilesTable, Repo
from sancho.db import queries, connection


def load_into_db(nodes: ASTnodesTable, repo: Repo):

    repo_id = queries.repo_exists(repo_path=repo.path)
    if repo_id is None:
        #repo_id = queries.create_repo(repo_path=repo.path, repo_name=repo.full_name)
        with connection:
            connection.execute("insert into git_repo(path,full_name) values (?,?) returning id",(repo.path,repo.full_name))

    file_id = queries.file_exists(repo_id=repo_id, local_path=nodes.full_path)
    if file_id is None:
        file_id = queries.create_file(repo_id=repo_id, local_path=nodes.full_path)

    for node in nodes.rows:
        queries.create_node(
            file_id=file_id,
            kind=node.kind,
            parent_id=node.parent_id,
            next_id=node.next_id,
            content=node.content,
        )


def test_load_into_db():
    from sancho.parsing import get_native_ast
    from sancho.etl import convert_parsed_text_to_nodes_table,REPOS_DIR

    repo = Repo(path="/ansible/ansible",full_name='')
    nodes = get_native_ast(REPOS_DIR+repo.path + "/setup.py")
    nodes = convert_parsed_text_to_nodes_table(nodes)
    load_into_db(nodes, repo)
