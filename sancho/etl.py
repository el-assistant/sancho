""" Contains function to download repos from github, and preprocess. ETL resources are located in PROJECT_ROOT/data/
"""
import glob
import os
from pathlib import Path

import dotenv
from loguru import logger

from sancho.defaults import *

dotenv.load_dotenv()

import sancho.model as model

REPOS_DIR = "data/repos/"
AST_CSV_DIR = "data/ast_csv/"
FILES_CSV_DIR = "data/files_csv/"


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






def make_files_table(repo: model.Repo) -> model.FilesTable:

    rootpath = Path(repo.path)

    def traverse(path: Path) -> model.FileRowFormat:
        for p in path.iter_dir():
            yield model.FileRowFormat(
                full_path=str(p),
                is_dir=p.is_dir(),
                parent_path=str(p.parent),
            )
            if p.is_dir():
                yield traverse(p)

    files_table = []
    files_table.append(model.FileRowFormat(full_path=str(rootpath), is_dir=True))
    files_table.extend(traverse(rootpath))
    return model.FilesTable(repo, files_table)





def load_parsed(repo: model.Repo):
    raise NotImplementedError  # TODO: implement it


def load_files(table: model.FilesTable):
    raise NotImplementedError  # TODO: implement it


def connect_files_and_AST(table: model.FilesTable):
    raise NotImplementedError  # TODO: implement it


def is_code_file(f: model.FileRowFormat) -> bool:
    from pathlib import Path

    p = Path(f.full_path)
    return p.suffix == ".py"


def load_repo(repo: model.Repo):
    filestable = make_files_table(repo)

    load_files(filestable)

    for f in filestable.rows:
        if is_code_file(f):
            load_parsed(get_parsed_as_csv(f.full_path))

    connect_files_and_AST(filestable)
