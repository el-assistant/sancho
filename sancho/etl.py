""" Contains function to download repos from github, and preprocess. ETL resources are located in PROJECT_ROOT/data/
"""
from loguru import logger
import dotenv, os, glob

dotenv.load_dotenv()


def clone_starred_python():
    from github import Github
    from git import Repo
    import git

    token = os.getenv("GH_ACCESS_TOKEN")
    assert token is not None

    g = Github(token)

    for r in g.search_repositories(query="language:python", sort="stars")[:500]:
        logger.info(f"Cloning {r.full_name=}")
        try:
            Repo.clone_from(
                r.html_url, f"data/repos/{r.full_name}", multi_options=["--depth 1"]
            )
        except git.exc.GitCommandError:
            logger.info(f"Failed to fetch {r.html_url}")


def parse_dir(path, parent_dir=None):

    from pathlib import Path
    from sancho.neo4jschema import DirNode, FileNode

    this = DirNode(name=path, project_root=True)
    this.save()
    if parent_dir:
        this.path.connect(parent_dir)

    p = Path(path)
    for f in p.iterdir():
        if f.is_dir():
            parse_dir(p.joinpath(f.name), this)
        elif f.suffix == ".py":
            parse_code(f, this)


def parse_code(f, path):
    from sancho.parsing import get_native_ast
    from sancho.neo4jconnecting import send_ast_to_neo4j
    from sancho.neo4jschema import FileNode

    new_file = FileNode(name=f.name).save()
    new_file.path.connect(path)
    ast_root = send_ast_to_neo4j(get_native_ast(f))
    new_file.ast_root.connect(ast_root)

    new_file.save()


def test_create_node1():
    from sancho.neo4jschema import DirNode
    from neomodel import db

    data = dict(path=None, name="hohohoho", project_root=True)
    with db.transaction:
        DirNode.create(data)
    with db.transaction:
        assert DirNode.nodes.get(name="hohohoho")


def test_create_node2():
    from sancho.neo4jschema import DirNode
    from neomodel import db

    logger.debug("start")
    for i in range(1000):
        DirNode(path=None, name=str(i), project_root=True).save()
    logger.debug(f"1000 dir nodes created")
    with db.transaction:
        for i in range(10000):
            DirNode(path=None, name=str(i), project_root=True).save()
    logger.debug(f"10000 dir nodes created in transaction")
    with db.transaction:
        DirNode.create(
            *[
                dict(path=None, name=str(i), project_root=True)
                for i in range(10000, 20000)
            ]
        )
    logger.debug(f"10000 dir nodes created in transaction using create method")


def test_create_node3():
    from sancho.neo4jschema import DirNode
    from neomodel import db

    def recurse(level=10, parent=None, name="base"):
        if level == 0:
            return
        this = DirNode(name=name, project_root=parent is None).save()
        if parent:
            this.path.connect(parent)
        for i in ["a", "b"]:
            recurse(level - 1, parent=this, name=i)
        return this

    recurse()


def test_create_node4():
    from sancho.neo4jschema import DirNode
    from neomodel import db

    def recurse(level=10, parent=None, name="base"):
        if level == 0:
            return
        this = DirNode(name=name, project_root=parent is None).save()
        if parent:
            this.path.connect(parent)
        for i in ["a", "b"]:
            recurse(level - 1, parent=this, name=i)
        return this

    recurse()


def test_parse_repo():
    path = glob.glob("data/repos/*/*/")[1]
    logger.debug(f"Start parsing repo {path}")

    parse_repo(path)
