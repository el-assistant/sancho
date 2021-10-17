from tree_sitter import Language, Parser
from git import Repo
from loguru import logger
from os import path


def main():
    target_path = f"resources/tree-sitter-python"
    if not path.exists(target_path):
        logger.info(f"{target_path=} does not exist. Cloning respective repo.")
        Repo.clone_from(
            "git@github.com:tree-sitter/tree-sitter-python.git",
            target_path,
            multi_options=["--depth=1"],
        )

    logger.info("Build tree-sitter-python")
    Language.build_library("languages.so", ["./resources/tree-sitter-python"])
