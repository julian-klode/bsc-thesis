#!/usr/bin/python
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

import re
import sys

FILE = sys.argv[1]
FIRST = re.compile(r"\\lstinputlisting\[(.*)firstline=([0-9]+)(.*)\]{%s}" %  FILE)
LAST = re.compile(r"\\lstinputlisting\[(.*)lastline=([0-9]+)(.*)\]{%s}" % FILE)
START = int(sys.argv[2])
END   = (int(sys.argv[3]), int(sys.argv[4]))
DIFF = (END[1] - END[0])

def sub_first(match):
    if int(match.group(2)) > END[0]:
        return "\\lstinputlisting[%sfirstline=%s%s]{%s}" % (match.group(1),
                                                            int(match.group(2)) + DIFF,
                                                            match.group(3),
                                                            FILE)

    return match.group(0)

def sub_last(match):
    if int(match.group(2)) > END[0]:
        return "\\lstinputlisting[%slastline=%s%s]{%s}" % (match.group(1),
                                                            int(match.group(2)) + DIFF,
                                                            match.group(3),
                                                            FILE)
    return match.group(0)


def subst(lines):
    for line in lines:
        oline = line
        line = FIRST.sub(sub_first, line)
        line = LAST.sub(sub_last, line)
        yield line

for file in sys.argv[5:]:
    with open(file) as lines:
        newlines = list(subst(lines))
    with open(file, "w") as target:
        for line in newlines:
            target.write(line)
