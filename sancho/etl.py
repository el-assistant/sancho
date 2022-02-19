""" Contains function to download repos from github, and preprocess. ETL resources are located in PROJECT_ROOT/data/
"""
from loguru import logger
import dotenv, os, glob
from pathlib import Path
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


def convert_parsed_text_to_csv(parsed: model.ParsedText) -> model.ASTnodesTable:
    assert parsed.tree and parsed.text

    path = Path(parsed.path).relative_to(REPOS_DIR)
    id_counter = 0

    def traverse(node: model.ASTnode):
        """Traverse breadth first, from right to left, yielding nodes in row format.

        local_id is created following the traversal order.
        """
        nonlocal id_counter

        parent_id = id_counter
        next_id = None
        for n in reversed(node.children):
            id_counter += 1
            yield model.ASTnodeRowFormat(
                full_path=path,
                local_id=id_counter,
                kind=n.kind,
                parent_id=parent_id,
                next_id=next_id,
                content=n.content,
            )
            next_id = id_counter

        for n in reversed(node.children):
            yield traverse(n)

    root = parsed.tree
    rows = []
    rows.append(
        model.ASTnodeRowFormat(
            full_path=path,
            local_id=id_counter,
            kind=root.kind,
        )
    )
    rows.extend(traverse(root))

    rows = collapse(rows, base_type=model.ASTnodeRowFormat)

    return model.ASTnodesTable(full_path=path, rows=rows)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]):
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in rows:
            writer.writerow(row._asdict())


def parse_as_csv(path: Path):
    """Writes to csv file the ASTnodes

    path is relative and it is used both for source and target files with the
    respective prefixes.

    """
    from sancho.parsing import get_native_ast

    native_ast = get_native_ast(Path(REPOS_DIR, path))
    nodestable = convert_parsed_text_to_csv(native_ast)

    fieldnames = model.ASTnodeRowFormat._fields
    csvpath = Path(AST_CSV_DIR, path).with_suffix(".csv")
    write_csv(csvpath, fieldnames, nodestable.rows)


def test_parse_as_csv():
    parse_as_csv(Path("ansible/ansible/setup.py"))


def parse_repo_ast_to_csv(repo: model.Repo):
    repopath = Path(REPOS_DIR, repo.path)
    for p in repopath.rglob(".py"):
        parse_as_csv(p.relative_to(REPOS_DIR))


def test_parse_repo_ast_to_csv():
    parse_repo_ast_to_csv(Path("ansible/ansible/setup.py"))


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


def parse_repo_dir_to_csv(repo: model.Repo):
    csvpath = Path(FILES_CSV_DIR, repo.path).with_suffix(".csv")
    fields = model.FileRowFormat._fields
    rows = make_files_table(repo).rows
    write_csv(csvpath, fields, rows)


def test_parse_repo_dir_to_csv():
    parse_repo_dir_to_csv(model.Repo(path="ansible/ansible/"))



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
