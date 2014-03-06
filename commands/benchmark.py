"""
Benchmark commands
"""
import os
import re
import subprocess
import sys
from reticular import argument, global_arg
from base import compile

ARGUMENTS = [
    global_arg('-a', '--arg', help='Defines an argument to pass to the executable', action='append'),
    global_arg('-c', '--cases', help='Number of cases (default: %(default)s)', default=20, type=int),
    global_arg('-e', '--executions', help='Number of executions per case (default: %(default)s)', default=1)
]


@argument('prog_file', help='File of the program to benchmark')
def full(prog_file, **kwargs):
    """
    Compiles, checks differences and generates stats and graphs
    """
    if not os.path.isfile(prog_file):
        raise RuntimeError('File not found: %s' % prog_file)

    executables = [
        compile(prog_file),
        compile(prog_file, olevel=1),
        compile(prog_file, olevel=3, native=True)
    ]

    for executable in executables:
        stats(executable, **kwargs)


@argument('executable', help='Executable file')
@argument('-q', '--quiet', help="Don't print the stats table", action='store_true')
def stats(executable, arg=None, cases=20, executions=1, quiet=False):
    """
    Generates stats with the real time
    """
    name, ext = os.path.splitext(executable)

    if arg is None:
        arg = []

    print "Generating stats for %s..." % executable
    with open("%s.stats" % name, 'w') as f:
        for i in xrange(1, cases+1):
            args = [eval(a) for a in arg]
            times = [run(executable, *args) for _ in xrange(executions)]
            row_id = args[0] if args else i
            row = "%d %.4f\n" % (row_id, sum(times)/executions)

            f.write(row)

            if not quiet:
                sys.stdout.write(row)


def run(exe, *args):
    cmd = ['time', '-f', 'fast|%e|fast', "./%s" % exe]
    cmd.extend(map(str, args))

    process = subprocess.Popen(cmd, stdout=open("/dev/null"), stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode:
        raise RuntimeError("Error when executing %s with args: %s" % (exe, args))

    elapsed = float(re.search(r'fast\|(\d+\.\d+)\|fast', err).group(1))
    return elapsed
