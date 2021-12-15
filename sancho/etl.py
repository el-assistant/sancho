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


def parse_repo(path, parent_dir=None):

    from pathlib import Path
    from sancho.parsing import get_native_ast
    from sancho.neo4jconnecting import send_ast_to_neo4j
    from sancho.neo4jschema import DirNode, FileNode

    if parent_dir is None:
        parent_dir = DirNode(path=None, name=path, project_root=True)
        parent_dir.save()

    p = Path(path)
    for f in p.iterdir():
        if f.is_dir():
            new_dir = DirNode(
                path=parent_dir,
                name=f.name,
            )
            new_dir.save()
            parse_repo(p.joinpath(f.name))
        elif f.suffix == ".py":
            ast_root = send_ast_to_neo4j(get_native_ast(f))
            new_file = FileNode(path=parent_dir, name=f.name, ast_root=ast_root)
            new_file.save()


def test_parse_repo():
    path = glob.glob("data/repos/*/*/")[1]
    parse_repo(path)
