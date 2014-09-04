#!/usr/bin/python3
#
# change-block-length.py - Adjust lstinputlisting to block length changes
#
# Copyright 2014 Julian Andres Klode <klode@mathematik.uni-marburg.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys
import subprocess
import glob


TEXFILES = glob.glob("*.tex") + glob.glob("*/*.tex")
REGEX = r"\\lstinputlisting\[%s%s=%s%s\]{%s}"
QUERY = "\\lstinputlisting[%s%s=%s%s]{%s}"
DIFFREGEX = r"^\+\+\+ b/(.*)|^@@ -([0-9]+),([0-9]+) \+([0-9]+),([0-9]+) @@"
DIFFRE = re.compile(DIFFREGEX, re.M)


def apply_hunk(fname, start, end_old, end_new):
    """Apply a change in block length to the LaTeX files."""
    diff = (end_new - end_old)
    first = REGEX % ("(.*)", "firstline", "([0-9]+)", "(.*)", fname)
    last = REGEX % ("(.*)", "lastline", "([0-9]+)", "(.*)", fname)

    if end_old == end_new:
        return

    def sub_first(match):
        if int(match.group(2)) > start  and int(match.group(2)) < end_old:
            print("Warning: Line %s might need manual change" % match.group(0))
        if int(match.group(2)) > end_old:
            return QUERY % (match.group(1), "firstline",
                            int(match.group(2)) + diff, match.group(3), fname)

        return match.group(0)

    def sub_last(match):
        if int(match.group(2)) > start  and int(match.group(2)) < end_old:
            print("Warning: Line %s might need manual change" % match.group(0))
        if int(match.group(2)) > end_old:
            return QUERY % (match.group(1), "lastline",
                            int(match.group(2)) + diff, match.group(3), fname)

        return match.group(0)

    def subst(lines):
        for line in lines:
            oline = line
            line = re.sub(first, sub_first, line)
            line = re.sub(last, sub_last, line)
            yield line

    for file in TEXFILES:
        with open(file) as lines:
            newlines = list(subst(lines))
        with open(file, "w") as target:
            for line in newlines:
                target.write(line)


def main_git():
    """Determines and applies block length changes using git."""
    proc = subprocess.Popen(["git", "diff", "scala"], stdout=subprocess.PIPE)
    out = proc.communicate()[0].decode()

    RE = re.compile("([-+])Subproject commit (.*)")
    frm = None
    to = None
    for mode, commit in RE.findall(out):
        if mode == "-":
            frm = commit
        elif mode == "+":
            to = commit
        else:
            raise ValueError("Unkown mode: %s" % mode)
    if frm is None or to is None:
        raise ValueError("Cannot calculate diff from %s to %s" % (frm, to))

    if "dirty" in to:
        to = []
    else:
        to = [to]
    proc = subprocess.Popen(["git", "-C", "scala", "diff", "-U1", frm] + to,
                            stdout=subprocess.PIPE)
    diff = proc.communicate()[0].decode()
    fname = None

    for path, start1, lines1, start2, lines2 in DIFFRE.findall(diff):
        if path:
            fname = path
        else:
            # We already applied previous changes, so the new start value
            # (that is, start2) is the one we are interested in.
            apply_hunk("scala/" + fname, int(start2),
                       int(start2) + int(lines1),
                       int(start2) + int(lines2))


def main(argv):
    """If no arguments are given, this determines the changes using git."""
    if len(argv) == 1:
        return main_git()

    try:
        start = int(argv[2])
        end_old = int(argv[3])
        end_new = int(argv[4])
    except Exception as e:
        print("Usage: %s <SOURCE fname> <START OF BLOCK> " +
              "<OLD END OF BLOCK> <NEW END>", file=sys.stderr)
        sys.exit(1)

    apply_hunk(argv[1], start, end_old, end_new)


if __name__ == '__main__':
    main(sys.argv)
