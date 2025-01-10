# src/lmsh/github_utils.py

import os
import sys
from github import Github, GithubException

def get_github_client() -> Github:
    """Authenticate and return a GitHub client."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)
    return Github(token)

def get_organization(client: Github, org_id: str):
    """Retrieve the GitHub organization or exit on failure."""
    try:
        org = client.get_organization(org_id)
        return org
    except GithubException as e:
        print(f"Error: Could not access organization '{org_id}': {e}")
        sys.exit(1)

def get_team(org, classroom_id: str):
    """
    Retrieve the GitHub team by ID or name.

    :param org: GitHub organization object
    :param classroom_id: Team ID (integer) или название (строка)
    :return: GitHub Team object
    """
    try:
        if classroom_id.isdigit():
            team = org.get_team(int(classroom_id))
        else:
            teams = org.get_teams()
            team = next((t for t in teams if t.name.lower() == classroom_id.lower()), None)
            if not team:
                print(f"Error: Team with name '{classroom_id}' not found in organization '{org.login}'.")
                sys.exit(1)
        return team
    except GithubException as e:
        print(f"Error: Could not retrieve team '{classroom_id}': {e}")
        sys.exit(1)
