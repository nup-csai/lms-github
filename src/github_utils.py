# src/lmsh/github_utils.py

import os
import sys
from github import Github, GithubException
import xml.etree.ElementTree as ET
import requests
import logging

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
    :param classroom_id: Team ID (integer) or name (string)
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

def parse_junit_xml(xml_content: str) -> float:
    """
    Parse JUnit XML from the string `xml_content`.
    Return the percentage of passed tests (0..100).
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logging.error(f"XML Parse Error: {e}")
        return 0.0

    total = 0
    passed = 0

    # Handle both <testsuite> and <testsuites>
    if root.tag == 'testsuites':
        for testsuite in root.findall('testsuite'):
            for testcase in testsuite.findall('testcase'):
                total += 1
                if not any(child.tag in ['failure', 'error', 'skipped'] for child in testcase):
                    passed += 1
    elif root.tag == 'testsuite':
        for testcase in root.findall('testcase'):
            total += 1
            if not any(child.tag in ['failure', 'error', 'skipped'] for child in testcase):
                passed += 1
    else:
        logging.warning("Unknown root tag in JUnit XML.")

    if total == 0:
        logging.warning("No tests found in JUnit XML.")
        return 0.0

    score_percent = (passed / total) * 100
    logging.info(f"Total tests: {total}, Passed tests: {passed}, Score: {score_percent}%")
    return score_percent

def download_artifact(artifact, headers):
    """
    Download an artifact using its archive_download_url.
    Return the bytes of the zip archive.
    """
    url = artifact.archive_download_url
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download artifact: HTTP {response.status_code}")


from nacl import encoding, public
import base64

def encrypt_secret(public_key_str: str, secret_value: str) -> str:
    """
    Encrypt a secret value using the repository's public key.

    :param public_key_str: Repository public key (Base64-encoded)
    :param secret_value: Secret value
    :return: Encrypted secret value (Base64-encoded)
    """
    public_key_bytes = public_key_str.encode("utf-8")
    public_key_obj = public.PublicKey(public_key_bytes, encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")