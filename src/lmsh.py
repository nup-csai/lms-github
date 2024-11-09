#!/usr/bin/env python3
"""
LMS Helper (lmsh) 
"""

import argparse
import sys
from typing import Optional, List

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
    """
    print("create_classroom command not implemented yet")

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
    print("create_assignment command not implemented yet")

def grade_assignment(args: argparse.Namespace) -> None:
    """
    Grade submitted assignments.
    Expected parameters:
    - assignment_id: ID of the assignment to grade
    - student_id: Optional specific student ID to grade
    - auto: Flag to enable automatic grading if available
    """
    print("grade_assignment command not implemented yet")

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
    create_assignment_parser.add_argument("--github-id", required=True, help="Student's GitHub ID")
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
