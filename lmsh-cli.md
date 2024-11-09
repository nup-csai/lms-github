# LMS Helper (lmsh) Documentation

`lmsh` is a command-line tool designed to automate common Learning Management System (LMS) tasks. This guide covers installation, usage, and available commands.

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Commands](#commands)
  - [Version](#version)
  - [Classroom Management](#classroom-management)
  - [Assignment Management](#assignment-management)
- [Examples](#examples)

## Installation

Ensure you have Python 3.x installed on your system. The script can be run directly:

```bash
chmod +x lmsh.py
./lmsh.py [command] [options]
```

Or using Python:

```bash
python3 lmsh.py [command] [options]
```

## Basic Usage

To see available commands:
```bash
./lmsh.py --help
```

Each command has its own help menu accessible via:
```bash
./lmsh.py [command] --help
```

## Commands

### Version
Display the current version of lmsh:
```bash
./lmsh.py version
```

### Classroom Management

#### Create a Classroom
Create a new classroom with specified parameters:
```bash
./lmsh.py classroom create --name "Course Name" --course-code "CS101" [--description "Course description"]
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
./lmsh.py assignment create \
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
./lmsh.py assignment grade \
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
./lmsh.py classroom create \
    --name "Introduction to Computer Science" \
    --course-code "CS101" \
    --description "Fall 2024 - Introduction to programming concepts"
```

2. Creating an assignment with all options:
```bash
./lmsh.py assignment create \
    --classroom-id "CS101-2024" \
    --title "Midterm Project" \
    --description "Build a simple command-line application" \
    --due-date "2024-10-15" \
    --points 100
```

3. Grading assignments automatically:
```bash
./lmsh.py assignment grade \
    --assignment-id "MIDTERM-2024" \
    --auto
```

4. Grading a specific student's assignment:
```bash
./lmsh.py assignment grade \
    --assignment-id "MIDTERM-2024" \
    --student-id "STUDENT456"
```

## Note

This is version 0.1.0 of the tool. Some commands are marked as "not implemented yet" and will be added in future versions. The basic command-line interface and argument parsing is set up, but the actual implementation of classroom creation, assignment management, and grading functionality is pending.