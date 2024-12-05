#!/usr/bin/env python3
"""
LMS Helper (lmsh) 
"""

import argparse
import sys
from typing import Optional, List
import os
from github import Github, GithubException


__version__ = "0.1.0"

def version_command(args: argparse.Namespace) -> None:
    """Display the current version of lmsh."""
    print(f"lmsh version {__version__}")

def create_classroom(args: argparse.Namespace) -> None:
    """
    Create a new classroom with specified parameters.
    Expected parameters:
    - name: Classroom name
    - description: Classroom description
    - course_code: Course identifier
    - org_id: GitHub organization ID/name
    """
    # Get GitHub token from environment variable
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    # Authenticate with GitHub API
    g = Github(token)

    # Get the organization
    try:
        org = g.get_organization(args.org_id)
    except GithubException as e:
        print(f"Error: Could not access organization '{args.org_id}': {e}")
        sys.exit(1)

    # Prepare team details
    team_name = args.name
    team_description = args.description if args.description else ''
    team_description += f"\nCourse Code: {args.course_code}"

    # Check if team already exists
    existing_teams = org.get_teams()
    for team in existing_teams:
        if team.name == team_name:
            print(f"Error: A classroom with the name '{team_name}' already exists.")
            sys.exit(1)

    # Create the team (classroom)
    try:
        team = org.create_team(
            name=team_name,
            description=team_description,
            privacy='closed',
            permission='push'
        )
        print(f"Classroom '{team_name}' created successfully.")
    except GithubException as e:
        print(f"Error: Could not create classroom '{team_name}': {e}")
        sys.exit(1)

def create_assignment(args: argparse.Namespace) -> None:
    """
    Create a new assignment in specified classroom.
    Expected parameters:
    - classroom_id: ID of the target classroom
    - title: Assignment title
    - description: Assignment description
    - due_date: Assignment due date (YYYY-MM-DD)
    - points: Maximum points available
    - github-id: Student's GitHub ID
    - org-id: GitHub organization ID/name
    """
    # Get GitHub token from environment variable
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    # Authenticate with GitHub API
    g = Github(token)

    # Get the organization
    try:
        org = g.get_organization(args.org_id)
    except GithubException as e:
        print(f"Error: Could not access organization '{args.org_id}': {e}")
        sys.exit(1)

    # Get the classroom team
    try:
        org = g.get_organization(args.org_id)
    except GithubException as e:
        print(f"Error: Could not access organization '{args.org_id}': {e}")
        sys.exit(1)

        # Получение команды (класса) по ID или названию
    team = None
    if args.classroom_id.isdigit():
        try:
            team = org.get_team(int(args.classroom_id))
        except GithubException as e:
            print(f"Error: Could not access team with ID '{args.classroom_id}': {e}")
            sys.exit(1)
    else:
        try:
            teams = org.get_teams()
            for t in teams:
                if t.name.lower() == args.classroom_id.lower():
                    team = t
                    break
            if not team:
                print(f"Error: Team with name '{args.classroom_id}' not found in organization '{args.org_id}'.")
                sys.exit(1)
        except GithubException as e:
            print(f"Error: Could not retrieve teams: {e}")
            sys.exit(1)

    # Define repository name (e.g., "Assignment-CS101-Midterm-Project")
    repo_name = f"Assignment-{args.course_code}-{args.title.replace(' ', '-')}"

    # Check if repository already exists
    try:
        repo = org.get_repo(repo_name)
        print(f"Error: Repository '{repo_name}' already exists.")
        sys.exit(1)
    except GithubException:
        pass  # Repository does not exist, proceed to create

    # Prepare repository description
    repo_description = args.description.replace('\n', ' ') if args.description else ''
    details = []
    if args.due_date:
        details.append(f"Due Date: {args.due_date}")
    if args.points:
        details.append(f"Points: {args.points}")
    if details:
        # Добавляем дополнительные детали через вертикальную черту
        repo_description += f" | {' | '.join(details)}" if repo_description else " | ".join(details)

    # Create the repository
    try:
        repo = org.create_repo(
            name=repo_name,
            description=repo_description,
            private=True,
            has_issues=True,
            has_projects=True,
            has_wiki=False
        )
        print(f"Repository '{repo_name}' created successfully.")
    except GithubException as e:
        print(f"Error: Could not create repository '{repo_name}': {e}")
        sys.exit(1)

    # Add the classroom team to the repository with push access
    try:
        team.add_to_repos(repo)
        print(f"Team '{team.name}' has been granted push access to '{repo_name}'.")
    except GithubException as e:
        print(f"Error: Could not add repository '{repo_name}' to team '{team.name}': {e}")
        sys.exit(1)

    # Optionally, initialize the repository with a README
    try:
        repo.create_file(
            path="README.md",
            message="Initial commit with assignment details",
            content=f"# {args.title}\n\n{args.description}\n\n**Due Date**: {args.due_date}\n**Points**: {args.points}"
        )
        print(f"README.md created in repository '{repo_name}'.")
    except GithubException as e:
        print(f"Error: Could not create README.md in repository '{repo_name}': {e}")
        sys.exit(1)
    print("create_assignment command not implemented yet")

def grade_assignment(args: argparse.Namespace) -> None:
    """
    Grade submitted assignments.
    Expected parameters:
    - assignment_id: ID of the assignment to grade
    - student_id: Optional specific student ID to grade
    - auto: Flag to enable automatic grading if available
    """

def setup_argparse() -> argparse.ArgumentParser:
    """Configure and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="LMS Helper - Automate common LMS tasks",
        prog="lmsh"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    version_parser = subparsers.add_parser("version", help="Display lmsh version")
    version_parser.set_defaults(func=version_command)

    # Classroom commands
    classroom_parser = subparsers.add_parser("classroom", help="Classroom management commands")
    classroom_subparsers = classroom_parser.add_subparsers(dest="classroom_command")

    # classroom create command
    create_classroom_parser = classroom_subparsers.add_parser("create", help="Create a new classroom")
    create_classroom_parser.add_argument("--name", required=True, help="Name of the classroom")
    create_classroom_parser.add_argument("--description", help="Classroom description")
    create_classroom_parser.add_argument("--course-code", required=True, help="Course identifier")
    create_classroom_parser.add_argument("--org-id", required=True, help="Organization ID/name")
    create_classroom_parser.set_defaults(func=create_classroom)

    # Assignment commands
    assignment_parser = subparsers.add_parser("assignment", help="Assignment management commands")
    assignment_subparsers = assignment_parser.add_subparsers(dest="assignment_command")

    # assignment create command
    create_assignment_parser = assignment_subparsers.add_parser("create", help="Create a new assignment")
    create_assignment_parser.add_argument("--classroom-id", required=True, help="ID of the target classroom")
    create_assignment_parser.add_argument("--title", required=True, help="Assignment title")
    create_assignment_parser.add_argument("--description", help="Assignment description")
    create_assignment_parser.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    create_assignment_parser.add_argument("--points", type=int, help="Maximum points available")
    create_assignment_parser.add_argument("--course-code", required=True, help="Course code associated with the assignment")
    # create_assignment_parser.add_argument("--github-id", required=True, help="Student's GitHub ID")
    create_assignment_parser.add_argument("--org-id", required=True, help="GitHub organization ID/name")
    create_assignment_parser.set_defaults(func=create_assignment)

    # assignment grade command
    grade_assignment_parser = assignment_subparsers.add_parser("grade", help="Grade submitted assignments")
    grade_assignment_parser.add_argument("--assignment-id", required=True, help="ID of the assignment to grade")
    grade_assignment_parser.add_argument("--student-id", help="Specific student ID to grade")
    grade_assignment_parser.add_argument("--auto", action="store_true", help="Enable automatic grading if available")
    grade_assignment_parser.set_defaults(func=grade_assignment)

    return parser

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = setup_argparse()
    parsed_args = parser.parse_args(args)

    if not hasattr(parsed_args, "command") or not parsed_args.command:
        parser.print_help()
        return 1

    if parsed_args.command == "classroom" and not parsed_args.classroom_command:
        parser.parse_args(["classroom", "-h"])
        return 1

    if parsed_args.command == "assignment" and not parsed_args.assignment_command:
        parser.parse_args(["assignment", "-h"])
        return 1

    parsed_args.func(parsed_args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
