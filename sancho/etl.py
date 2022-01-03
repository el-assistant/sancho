""" Contains function to download repos from github, and preprocess. ETL resources are located in PROJECT_ROOT/data/
"""
from loguru import logger
import dotenv, os, glob

dotenv.load_dotenv()

import sancho.model as model


def clone_starred_python():
    """Entry point function that fetches whole repositories into local storage."""
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


def convert_parsed_text_to_csv(parsed: model.ParsedText) -> model.ASTnodesTable:
    assert parsed.tree and parsed.text
    raise NotImplementedError  # TODO: implement it


def get_parsed_as_csv(path: str) -> model.ASTnodesTable:
    from sancho.parsing import get_native_ast

    return convert_parsed_text_to_csv(get_native_ast(path))


def load_parsed(parsed: model.ASTnodesTable):
    raise NotImplementedError  # TODO: implement it


def load_files(table: model.FilesTable):
    raise NotImplementedError  # TODO: implement it


def connect_files_and_AST(table: model.FilesTable):
    raise NotImplementedError  # TODO: implement it


def load_repo(repo: model.Repo):
    def make_files_table(repo: model.Repo) -> model.FilesTable:
        raise NotImplementedError  # TODO: implement it

    def is_code_file(f: model.FileRowFormat) -> bool:
        from pathlib import Path

        p = Path(f.full_path)
        return p.suffix == ".py"

    filestable = make_files_table(repo)

    load_files(filestable)

    for f in filestable.rows:
        if is_code_file(f):
            load_parsed(get_parsed_as_csv(f.full_path))

    connect_files_and_AST(filestable)
