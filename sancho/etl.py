""" Contains function to download repos from github, and preprocess. ETL resources are located in PROJECT_ROOT/data/
"""
import dotenv, os

dotenv.load_dotenv()
token = os.getenv("GH_ACCESS_TOKEN")
assert token is not None

from github import Github
from git import Repo


g = Github(token)


def clone_starred_python():
    for r in g.search_repositories(query="language:python", sort="stars")[:500]:
        Repo.clone_from(
            r.html_url, f"data/repos/{r.full_name}", multi_options=["--depth=1"]
        )
