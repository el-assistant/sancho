""" Contains function to download repos from github, and preprocess. ETL resources are located in PROJECT_ROOT/data/
"""
from loguru import logger
import dotenv, os

dotenv.load_dotenv()
token = os.getenv("GH_ACCESS_TOKEN")
assert token is not None

from github import Github
from git import Repo
import git

g = Github(token)


def clone_starred_python():
    for r in g.search_repositories(query="language:python", sort="stars")[:500]:
        logger.info(f"Cloning {r.full_name=}")
        try:
            Repo.clone_from(
                r.html_url, f"data/repos/{r.full_name}", multi_options=["--depth 1"]
            )
        except git.exc.GitCommandError:
            logger.info(f"Failed to fetch {r.html_url}")
