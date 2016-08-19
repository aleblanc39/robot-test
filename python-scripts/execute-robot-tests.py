#!/usr/bin/env python

"""

This script will execute tests written in the Robot Framework. It was designed
to make it easy to execute the tests from the PyCharm IDE. To erxecute from PyCharm
you first need to condigure the IDE as follows:

1) Go to File->Settings->Tools->External Tools
2) Your will define two new tools, one for running a single test, and one for all the tests in the suite. The only difference
   between the two will be the *name* and *parameter* entries.
   a) For running a single test, use these values in the **Tool Settings** section at the bottom
      Program: Python
      Parameters: [path-to-script]/execute-robot-tests.py --filename $FilePath$ --line-no $LineNumber$ --top-directory $ProjectFileDir$ --relative-filename $FilePathRelativeToProjectRoot$  --project-name $ProjectName$
      Working Directory: ${ProjectFileDir}
   b) For running all the tests in a suite, assign a different name and update the parameters entry to:
       Parameters: [path-to-script]/execute-robot-tests.py --filename $FilePath$ --line-no $LineNumber$ --top-directory $ProjectFileDir$ --relative-filename $FilePathRelativeToProjectRoot$  --project-name $ProjectName$ --single-test

3) To execute a single test right-click anywhere in the code for this test, go to *external tools* and select the appropriate tool based on
   the name that yuou assigned. To run a test on the whole suite click anywhere in the file.

"""

import subprocess
import argparse
from os import chdir
from os import name as os_name
from os import sep as os_sep
import sys
import os.path
import time
import threading

from datetime import datetime

execution_done = False


def main():
    global execution_done
    parser = argparse.ArgumentParser(description='Execute robot tests.')
    parser.add_argument("--filename", dest='file_path', nargs='+')
    parser.add_argument("--line-no", dest='line_number', type=int)
    parser.add_argument("--top-directory", dest='top_directory', nargs='+')
    parser.add_argument("--relative-filename", dest="relative_filename", nargs="+")
    parser.add_argument("--project-name", dest="project_name", nargs='+')
    parser.add_argument("--single-test", action="store_true")
    args = parser.parse_args()

    output_directory = os.path.join(' '.join(args.top_directory), "Output_Files",
                                    str(datetime.now().strftime('%Y%m%d-%H%M%S')))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    else:
        [os.remove(os.path.join(output_directory, f)) for f in os.listdir(output_directory)]

    debug_file = os.path.join(output_directory, "robot-debug.txt")
    suite_name = extract_suite_name(' '.join(args.relative_filename), ' '.join(args.project_name))
    params = [
        '--outputdir',
        output_directory,
        "--loglevel",
        "INFO",
        "--debugfile",
        debug_file,
        '--suite',
        suite_name
    ]

    if args.single_test:
        try:
            test_name = extract_test_name(' '.join(args.file_path), args.line_number - 1)
            params.extend(['--test', suite_name + '.' + test_name])
        except Exception as e:
            print "Problem with Single test case: ", e
            exit()


    params.append(' '.join(args.top_directory))
    t2 = threading.Thread(target=monitor_debug_file, args=[debug_file])
    t2.start()

    chdir(' '.join(args.top_directory))
    output_file = open(os.path.join(output_directory, "std_output.txt"), mode="w")
    err_file = open(os.path.join(output_directory, "std_err.txt"), mode="w")


    if os_name == "posix":
        pybot = 'pybot'
    else:
        pybot = 'pybot.bat'
    my_args = [pybot] + params

    sys.stdout.flush()
    subprocess.call(my_args, stdout=output_file.fileno(), stderr=err_file.fileno())
    execution_done = True

    t2.join()
    output_file.close()
    err_file.close()


def extract_suite_name(file_path, project_name):
    """
    Create the package name from a filename that contains
    the whole path.
    """

    suite_name = str(project_name) + "."
    suite_name = suite_name + os.path.splitext(str(file_path).replace(os_sep, "."))[0]
    return suite_name


def print_data(lines):
    for x in lines:
        if 'START KW' not in x and 'END KW' not in x and ' DEBUG ' not in x:
            sys.stdout.write(x)


def monitor_debug_file(debug_file):
    global execution_done
    while not os.path.isfile(debug_file) and not execution_done:
        time.sleep(1)

    # If the execution is done but there is no debug file then there was an early error, such as
    # invoking on a files that is not a robot framework file, or non-existing file.
    if not os.path.isfile(debug_file) and execution_done:
        # This is executed in a separate thread. Can't really raise exception.
        print ("Problem encountered in execution: please look at your Output_Files/std_err.txt")
        return

    with open(debug_file, "r") as f:
        lines = f.readlines()
        last_pos = f.tell()
        print_data(lines)

    while not execution_done:
        with open(debug_file, "r") as f:
            time.sleep(0.1)
            f.seek(last_pos)
            new_data = f.readlines()
            last_pos = f.tell()
            print_data(new_data)


def extract_test_name(filename, line_number):
    """
    Returns the name of the test defined in the given file at
    the given line number

    :param filename: The name of the file containing the suite
    :type filename: string
    :param line_number: The line number fro which
    :type line_number: Int
    :return: Name of the test defined at the line number. None
             if he line is outside any test.
    :rtype:
    """

    with open(filename) as f:
        lines = f.readlines()
    tests_begins = next((x for x in xrange(len(lines)) if lines[x].startswith("*** Test Cases ***")), -1)
    if tests_begins == -1:
        raise Exception("No Test Case Section")
    tests_ends = next((x for x in xrange(tests_begins + 1, len(lines)) if lines[x][0:3] == "***"), len(lines))

    if line_number <= tests_begins or line_number >= tests_ends:
        raise Exception("Outside of test cases section")

    test_case_line = next(
        (x for x in xrange(line_number, tests_begins, -1) if len(lines[x]) > 1 and lines[x][0] != ' '), -1)
    if test_case_line == -1:
        raise Exception("No test case found in Test Cases section")

    return str(lines[test_case_line]).strip()


if __name__ == "__main__":
    main()
