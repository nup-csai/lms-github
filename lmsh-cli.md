# LMS Helper (lmsh)

`lmsh` is a command-line tool designed to automate common Learning Management System (LMS) tasks. 

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Commands](#commands)
  - [Version](#version)
  - [Classroom Management](#classroom-management)
  - [Assignment Management](#assignment-management)
- [Examples](#examples)

## Installation
TBD

## Basic Usage

TBD

## Commands

### Version
Display the current version of lmsh:
```bash
$lmsh.py version
```

### Classroom Management

#### Create a Classroom
Create a new classroom with specified parameters:
```bash
$lmsh classroom create --name "Course Name" --course-code "CS101" [--description "Course description"]
```

Required parameters:
- `--name`: Name of the classroom
- `--course-code`: Course identifier

Optional parameters:
- `--description`: Classroom description

### Assignment Management

#### Create an Assignment
Create a new assignment in a specified classroom:
```bash
$lmsh assignment create \
    --classroom-id "CLASS123" \
    --title "Assignment Title" \
    [--description "Assignment description"] \
    [--due-date "2024-12-31"] \
    [--points 100]
```

Required parameters:
- `--classroom-id`: ID of the target classroom
- `--title`: Assignment title

Optional parameters:
- `--description`: Assignment description
- `--due-date`: Due date in YYYY-MM-DD format
- `--points`: Maximum points available

#### Grade Assignments
Grade submitted assignments for a specific assignment:
```bash
$lmsh assignment grade \
    --assignment-id "ASSGN123" \
    [--student-id "STUDENT123"] \
    [--auto]
```

Required parameters:
- `--assignment-id`: ID of the assignment to grade

Optional parameters:
- `--student-id`: Specific student ID to grade
- `--auto`: Enable automatic grading if available

## Examples

1. Creating a new classroom:
```bash
$lmsh classroom create \
    --name "Introduction to Computer Science" \
    --course-code "CS101" \
    --description "Fall 2024 - Introduction to programming concepts"
```

2. Creating an assignment with all options:
```bash
$lmsh assignment create \
    --classroom-id "CS101-2024" \
    --title "Midterm Project" \
    --description "Build a simple command-line application" \
    --due-date "2024-10-15" \
    --points 100
    --github_id Student's GitHub ID
    --org_id GitHub organization ID/name
```

3. Grading assignments automatically:
```bash
$lmsh assignment grade \
    --assignment-id "MIDTERM-2024" \
    --auto
```

4. Grading a specific student's assignment:
```bash
$lmsh assignment grade \
    --assignment-id "MIDTERM-2024" \
    --student-id "STUDENT456"
```
