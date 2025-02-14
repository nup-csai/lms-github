#!/usr/bin/env python3
"""
LMS Helper (lmsh) 
"""

import argparse
import sys
from typing import Optional, List
from github import GithubException
from github_utils import get_github_client, get_organization, get_team, parse_junit_xml, download_artifact, encrypt_secret
import logging
from datetime import datetime
import json
from textwrap import dedent
import zipfile
import io
import os
import xml.etree.ElementTree as ET
from nacl import encoding, public

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

__version__ = "0.1.0"

def version_command(args: argparse.Namespace) -> None:
    """Display the current version of lmsh."""
    logging.info(f"lmsh version {__version__}")

def validate_due_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def create_classroom(args: argparse.Namespace) -> None:
    """
    Create a new classroom with specified parameters.
    Expected parameters:
    - name: Classroom name
    - description: Classroom description
    - course_code: Course identifier
    - org_id: GitHub organization ID/name
    """
    client = get_github_client()
    org = get_organization(client, args.org_id)

    # Prepare team details
    team_name = args.name
    team_description = args.description if args.description else ''
    team_description += f"\nCourse Code: {args.course_code}"

    # Check if team already exists
    existing_teams = org.get_teams()
    for team in existing_teams:
        if team.name == team_name:
            logging.error(f"Error: A classroom with the name '{team_name}' already exists.")
            sys.exit(1)

    # Create the team (classroom)
    try:
        team = org.create_team(
            name=team_name,
            description=team_description,
            privacy='closed',
            permission='push'
        )
        logging.info(f"Classroom '{team_name}' created successfully.")
    except GithubException as e:
        logging.error(f"Error: Could not create classroom '{team_name}': {e}")
        sys.exit(1)


def create_assignment(args: argparse.Namespace) -> None:
    """
    Создаёт задание следующим образом:
      1. Создаёт (или использует существующий) приватный репозиторий с тестами: 'Assignment-{course_code}-{title}-tests'.
      2. Для каждого студента создаёт приватный репозиторий: 'Assignment-{course_code}-{title}-{student_login}'.
      3. Добавляет GitHub Actions workflow в студенческий репозиторий, который клонирует тестовый репозиторий и выполняет тесты.
      4. Добавляет секрет DOWNLOAD_TESTS_TOKEN в студенческий репозиторий для доступа к тестовому репозиторию.

    Параметры:
      --classroom-id  (str): Имя (или ID) GitHub Team, в котором состоят студенты
      --teacher-team  (str): Имя (или ID) GitHub Team преподавателей
      --title         (str): Название задания (Exam Project6)
      --course-code   (str): Код курса (CS101)
      --org-id        (str): GitHub организация (lmsh-test)
      --due-date      (str): Опционально, дедлайн
      --points        (int): Опционально, баллы
      --tests-dir     (str): Путь к локальной директории с тестовыми файлами
    """

    # 1. Получаем GitHub-клиент и организацию
    client = get_github_client()
    org = get_organization(client, args.org_id)

    # 2. Получаем team, где состоят студенты
    student_team = get_team(org, args.classroom_id)
    if not student_team:
        logging.error(f"Team '{args.classroom_id}' not found.")
        sys.exit(1)

    # 3. Получаем team преподавателей
    teacher_team = None
    if args.teacher_team:
        all_teams = org.get_teams()
        for t in all_teams:
            if t.name.lower() == args.teacher_team.lower():
                teacher_team = t
                break

    # 4. Проверка due_date
    if args.due_date and not validate_due_date(args.due_date):
        logging.error("Error: Invalid date format for --due-date. Use YYYY-MM-DD.")
        sys.exit(1)

    # 5. Создаём или получаем тестовый репозиторий
    tests_repo_name = f"Assignment-{args.course_code}-{args.title.replace(' ', '-')}-tests"
    try:
        try:
            tests_repo = org.get_repo(tests_repo_name)
            logging.info(f"Tests repository '{tests_repo_name}' already exists.")
        except GithubException:
            # Репозиторий не существует — создаём
            tests_repo_description = f"Tests for {args.title}"
            tests_repo = org.create_repo(
                name=tests_repo_name,
                description=tests_repo_description,
                private=True,
                has_issues=False,
                has_projects=False,
                has_wiki=False,
                auto_init=True  # создаёт начальный коммит с README.md
            )
            logging.info(f"Tests repository '{tests_repo_name}' created successfully.")

            # Добавляем Teacher Team (push-доступ)
            if teacher_team:
                try:
                    teacher_team.add_to_repos(tests_repo)
                    logging.info(
                        f"Teacher team '{teacher_team.name}' has push access to tests repo '{tests_repo_name}'.")
                except GithubException as e:
                    logging.error(f"Error adding teacher team to tests repo '{tests_repo_name}': {e}")

    except GithubException as e:
        logging.error(f"Could not create or access tests repo '{tests_repo_name}': {e}")
        sys.exit(1)

    # 6. Загружаем тестовые файлы в тестовый репозиторий
    if args.tests_dir:
        if not os.path.isdir(args.tests_dir):
            logging.error(f"Tests directory '{args.tests_dir}' does not exist or is not a directory.")
            sys.exit(1)

        # Получаем список всех файлов в тестовой директории
        for root, dirs, files in os.walk(args.tests_dir):
            for file in files:
                if file.endswith(".py"):  # предположим, что тесты на Python
                    file_path = os.path.join(root, file)
                    # Определяем путь в репозитории (относительно tests_repo)
                    relative_path = os.path.relpath(file_path, args.tests_dir)
                    repo_path = f"tests/{relative_path}".replace("\\", "/")  # для Windows путей

                    # Читаем содержимое файла
                    with open(file_path, "r") as f:
                        content = f.read()

                    try:
                        # Проверяем, существует ли уже файл
                        existing_file = tests_repo.get_contents(repo_path)
                        # Если существует, обновляем
                        tests_repo.update_file(
                            path=repo_path,
                            message=f"Update {repo_path}",
                            content=content,
                            sha=existing_file.sha
                        )
                        logging.info(f"Updated test file '{repo_path}' in tests repository.")
                    except GithubException as e:
                        if e.status == 404:
                            # Файл не существует — создаём
                            tests_repo.create_file(
                                path=repo_path,
                                message=f"Add {repo_path}",
                                content=content
                            )
                            tests_repo.create_file(
                                path="tests/__init__.py",
                                message=f"Add init",
                                content=""
                            )
                            logging.info(f"Added test file '{repo_path}' and init to tests repository.")
                        else:
                            logging.error(f"Error adding/updating test file '{repo_path}': {e}")
    else:
        logging.warning("No tests directory provided. Skipping uploading test files.")

    # 7. Получаем список участников (студентов)
    members = list(student_team.get_members())
    if not members:
        logging.info(f"No members found in team '{student_team.name}'. Nothing to do.")
        return

    # 8. Цикл по студентам
    for member in members:
        student_login = member.login
        student_repo_name = f"Assignment-{args.course_code}-{args.title.replace(' ', '-')}-{student_login}"

        # Проверяем, существует ли уже репозиторий
        try:
            _ = org.get_repo(student_repo_name)
            logging.info(f"Repo '{student_repo_name}' already exists. Skipping.")
            continue
        except GithubException:
            pass  # репозиторий не существует, создаём

        # Формируем описание репозитория
        repo_description = f"{args.title} for {student_login}"
        extra_details = []
        if args.due_date:
            extra_details.append(f"Due Date: {args.due_date}")
        if args.points:
            extra_details.append(f"Points: {args.points}")
        if extra_details:
            repo_description += " | " + " | ".join(extra_details)

        try:
            # Создаём приватный репозиторий
            repo = org.create_repo(
                name=student_repo_name,
                description=repo_description,
                private=True,
                has_issues=True,
                has_projects=True,
                has_wiki=False,
                auto_init=True  # создаёт начальный коммит с README.md
            )
            logging.info(f"Repository '{student_repo_name}' created successfully.")
        except GithubException as e:
            logging.error(f"Error: Could not create repository '{student_repo_name}': {e}")
            continue

        # Добавляем преподавательский team (если есть)
        if teacher_team:
            try:
                teacher_team.add_to_repos(repo)
                logging.info(f"Teacher team '{teacher_team.name}' has push access to '{student_repo_name}'.")
            except GithubException as e:
                logging.error(f"Error adding teacher team to '{student_repo_name}': {e}")

        # Добавляем студента как коллаборатора с push-доступом
        try:
            repo.add_to_collaborators(student_login, permission='push')
            logging.info(f"Student '{student_login}' added to '{student_repo_name}'.")
        except GithubException as e:
            logging.error(f"Error adding student '{student_login}' to '{student_repo_name}': {e}")

        # Обновляем README.md
        readme_content = dedent(f"""\
            # {args.title}

            Hello {student_login}!

            This is your private repository for the assignment.
            Due Date: {args.due_date if args.due_date else 'N/A'}
            Points: {args.points if args.points else 'N/A'}
        """)
        try:
            readme_file = repo.get_contents("README.md")
            repo.update_file(
                path=readme_file.path,
                message="Update README with assignment details",
                content=readme_content,
                sha=readme_file.sha
            )
            logging.info(f"README.md updated in '{student_repo_name}'.")
        except GithubException as e:
            logging.error(f"Error updating README in '{student_repo_name}': {e}")

        # 9. Добавляем секрет DOWNLOAD_TESTS_TOKEN в студенческий репозиторий
        # Предполагаем, что секрет DOWNLOAD_TESTS_TOKEN содержит Personal Access Token с read-доступом к tests_repo
        DOWNLOAD_TESTS_TOKEN = os.getenv("DOWNLOAD_TESTS_TOKEN")
        if not DOWNLOAD_TESTS_TOKEN:
            logging.warning("Environment variable DOWNLOAD_TESTS_TOKEN not set. Skipping secret creation.")
            continue

        # Создаём GitHub Actions workflow (autograde.yml)
        autograde_content = dedent(f"""
            name: Autograde

            on:
              push:
                branches: [main]
              pull_request:
                branches: [main]
            
            jobs:
              build-and-test:
                if: github.actor != 'lmsh-bot'
                runs-on: ubuntu-latest
                steps:
                  - name: Check out code
                    uses: actions/checkout@v3
                    with:
                      fetch-depth: 0  # Клонируем всю историю коммитов
            
                  - name: Install dependencies
                    run: |
                      pip install --upgrade pip
                      pip install pytest
            
                  - name: Count commits
                    id: commit_count
                    run: |
                      commit_count=$(git rev-list --count HEAD)
                      echo "commit_count=$commit_count" >> $GITHUB_OUTPUT
            
                  - name: Skip if only one commit
                    if: steps.commit_count.outputs.commit_count == '1'
                    run: echo "Skipping workflow because it's the initial commit."
            
                  - name: Checkout tests repository
                    if: steps.commit_count.outputs.commit_count != '1'
                    uses: actions/checkout@v3
                    with:
                      repository: lmsh-test/{tests_repo_name}
                      token: ${{{{ secrets.DOWNLOAD_TESTS_TOKEN }}}}
                      path: tests
            
                  - name: Create reports directory
                    if: steps.commit_count.outputs.commit_count != '1'
                    run: mkdir -p reports
            
                  - name: Run tests
                    if: steps.commit_count.outputs.commit_count != '1'
                    run: |
                      export PYTHONPATH=${{PYTHONPATH}}:$(pwd)
                      pytest --junitxml=reports/test_results.xml
            
                  - name: Upload test artifact
                    if: always() && steps.commit_count.outputs.commit_count != '1'
                    uses: actions/upload-artifact@v3
                    with:
                      name: junit-report
                      path: reports/test_results.xml
        """)

        try:
            repo.create_file(
                path=".github/workflows/autograde.yml",
                message="Add autograde workflow",
                content=autograde_content
            )
            logging.info(f"autograde.yml created in repository '{student_repo_name}'.")
        except GithubException as e:
            logging.error(f"Error creating autograde.yml in repository '{student_repo_name}': {e}")


        try:
            public_key = repo.get_public_key()
            encrypted_value = encrypt_secret(public_key.key, DOWNLOAD_TESTS_TOKEN)
            repo.create_secret("DOWNLOAD_TESTS_TOKEN", DOWNLOAD_TESTS_TOKEN)
            logging.info(f"Secret 'DOWNLOAD_TESTS_TOKEN' added to repository '{student_repo_name}'.")
        except GithubException as e:
            logging.error(f"Error adding secret to repository '{student_repo_name}': {e}")
        except Exception as e:
            logging.error(f"Unexpected error adding secret to repository '{student_repo_name}': {e}")


def grade_assignment(args: argparse.Namespace) -> None:
    """
    Собирает и выводит результаты автотестов для заданий по префиксу вида:
      'Assignment-{course_code}-{title.replace(' ', '-')}-{student_login}'

    Предполагается, что в репозитории студентов хранится файл GitHub Actions workflow,
    который при success/failure создаёт artifact 'junit-report' с файлом 'test_results.xml'.
    """

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logging.error("Environment variable GITHUB_TOKEN not set.")
        sys.exit(1)

    client = get_github_client()
    org = get_organization(client, args.org_id)

    # Формирование префикса репозиториев (пример: "Assignment-CS101-Exam-Project2-")
    prefix = f"Assignment-{args.course_code}-{args.title.replace(' ', '-')}-"

    # Получаем все репозитории организации
    try:
        all_repos = org.get_repos()
    except GithubException as e:
        logging.error(f"Could not list repositories for organization '{args.org_id}': {e}")
        sys.exit(1)

    # Фильтруем репозитории по префиксу
    target_repos = [repo for repo in all_repos if repo.name.startswith(prefix)]

    if not target_repos:
        logging.info(f"No matching repositories found for this assignment (prefix '{prefix}').")
        return

    logging.info(f"Found {len(target_repos)} repositories matching prefix '{prefix}'.")

    results = []

    # Заголовки для скачивания артефактов
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    for repo in target_repos:
        repo_name = repo.name
        logging.info(f"Processing repository '{repo_name}'...")

        try:
            # Получаем workflow runs на ветке main
            runs = repo.get_workflow_runs(branch="main")
            if runs.totalCount == 0:
                logging.info(f"No workflow runs found in '{repo_name}'. Score=0.")
                results.append({
                    "repo": repo_name,
                    "conclusion": None,
                    "score": 0,
                    "details": "No workflow runs found."
                })
                continue

            # Берём последний (самый свежий) workflow run
            latest_run = runs[0]
            run_id = latest_run.id
            status = latest_run.status        # e.g. completed, in_progress, queued
            conclusion = latest_run.conclusion or "in_progress"
            # conclusion может быть success, failure, neutral, cancelled, timed_out, action_required, stale

            logging.info(f"Latest run in '{repo_name}': status={status}, conclusion={conclusion} (Run ID={run_id})")

            # Если workflow run ещё не в статусе completed (in_progress, queued, cancelled и т.д.),
            # мы не можем собрать финальные результаты тестов
            if status != "completed":
                logging.info(f"Workflow run in '{repo_name}' has status='{status}', not 'completed'. Skipping scoring.")
                results.append({
                    "repo": repo_name,
                    "conclusion": conclusion,
                    "score": 0,
                    "details": f"Workflow run status={status}, not completed yet."
                })
                continue

            # Если conclusion не success/failure, считаем, что тесты не прошли корректно
            if conclusion not in ["success", "failure"]:
                logging.info(f"Workflow run in '{repo_name}' conclusion='{conclusion}' not in success/failure. Skipping.")
                results.append({
                    "repo": repo_name,
                    "conclusion": conclusion,
                    "score": 0,
                    "details": f"Workflow run conclusion={conclusion}, not success/failure."
                })
                continue

            # Если дошли сюда, run завершён (status=completed) и conclusion= success/failure
            # Теперь смотрим артефакты
            artifacts = latest_run.get_artifacts()
            if artifacts.totalCount == 0:
                logging.info(f"No artifacts found in '{repo_name}'. Score=0.")
                results.append({
                    "repo": repo_name,
                    "conclusion": conclusion,
                    "score": 0,
                    "details": "No artifacts found."
                })
                continue

            # Ищем artifact 'junit-report'
            junit_artifact = None
            for artifact in artifacts:
                if artifact.name == "junit-report":
                    junit_artifact = artifact
                    break

            if not junit_artifact:
                logging.info(f"Artifact 'junit-report' not found in '{repo_name}'. Score=0.")
                results.append({
                    "repo": repo_name,
                    "conclusion": conclusion,
                    "score": 0,
                    "details": "Artifact 'junit-report' not found."
                })
                continue

            # Пытаемся скачать артефакт
            try:
                zip_bytes = download_artifact(junit_artifact, headers)
            except Exception as e:
                logging.error(f"Failed to download artifact for '{repo_name}': {e}")
                results.append({
                    "repo": repo_name,
                    "conclusion": conclusion,
                    "score": 0,
                    "details": f"Failed to download artifact: {e}"
                })
                continue

            # Распаковываем zip-архив и ищем test_results.xml
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
                test_results_path = None
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith("test_results.xml"):
                        test_results_path = file_info.filename
                        break

                if not test_results_path:
                    logging.info(f"'test_results.xml' not found in artifact of '{repo_name}'. Score=0.")
                    results.append({
                        "repo": repo_name,
                        "conclusion": conclusion,
                        "score": 0,
                        "details": "test_results.xml not found in artifact."
                    })
                    continue

                # Читаем содержимое XML
                with zip_ref.open(test_results_path) as xml_file:
                    xml_content = xml_file.read().decode('utf-8')

            # Парсим JUnit XML
            score_percent = parse_junit_xml(xml_content)
            logging.info(f"Calculated score for '{repo_name}': {score_percent}%.")

            results.append({
                "repo": repo_name,
                "conclusion": conclusion,
                "score": score_percent,
                "details": f"Passed {score_percent}%.",
                "html_url": latest_run.html_url
            })

        except GithubException as e:
            logging.error(f"GitHub API error for '{repo_name}': {e}")
            results.append({
                "repo": repo_name,
                "error": str(e),
                "score": 0
            })
        except zipfile.BadZipFile as e:
            logging.error(f"Error unpacking artifact in '{repo_name}': {e}")
            results.append({
                "repo": repo_name,
                "error": "BadZipFile",
                "score": 0
            })
        except ET.ParseError as e:
            logging.error(f"Error parsing JUnit XML in '{repo_name}': {e}")
            results.append({
                "repo": repo_name,
                "error": "XML parse error",
                "score": 0
            })

    # Выводим JSON-отчёт
    output_json = json.dumps(results, indent=2, ensure_ascii=False)
    print(output_json)

    logging.info("Grading completed.")

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
    create_classroom_parser.add_argument("--org-id", required=True, help="Organization ID/name")
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
    create_assignment_parser.add_argument("--teacher-team", required=True, help="GitHub Teachers Team name or ID")
    create_assignment_parser.add_argument("--org-id", required=True, help="GitHub organization ID/name")
    create_assignment_parser.add_argument("--tests-dir", required=True, help="Tests for assignment")
    create_assignment_parser.add_argument("--description", help="Assignment description")
    create_assignment_parser.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    create_assignment_parser.add_argument("--points", type=int, help="Maximum points available")
    create_assignment_parser.add_argument("--course-code", required=True, help="Course code associated with the assignment")
    create_assignment_parser.add_argument("--github-id", nargs='+', help="Student's GitHub ID(s) to add to the repository")
    create_assignment_parser.set_defaults(func=create_assignment)

    # assignment grade command
    grade_assignment_parser = assignment_subparsers.add_parser("grade", help="Grade submitted assignments")
    grade_assignment_parser.add_argument("--classroom-id", required=True, help="ID of the target classroom")
    grade_assignment_parser.add_argument("--org-id", required=True, help="GitHub organization ID/name")
    grade_assignment_parser.add_argument("--title", required=True, help="Assignment title")
    grade_assignment_parser.add_argument("--course-code", required=True, help="Course code associated with the assignment")
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
