"""
Benchmark commands
"""
import os
import subprocess
import sys
import time
from core.utils import generate_graphs, swap_ext
from reticular import argument, global_arg, say
from base import compile

ARGUMENTS = [
    global_arg('-a', '--arg', help='Defines an argument to pass to the executable', action='append', default=[]),
    global_arg('-c', '--cases', help='Number of cases (default: %(default)s)', default=20, type=int),
    global_arg('-e', '--executions', help='Number of executions per case (default: %(default)s)', default=1)
]


@argument('original', help='Original source file')
@argument('optimized', help='Optimized source file', nargs='?')
def full(original, optimized=None, **kwargs):
    """
    Compiles, checks differences and generates stats and graphs
    """
    for prog_file in [original, optimized]:
        if prog_file:
            if not os.path.isfile(prog_file):
                raise RuntimeError('File not found: %s' % prog_file)

    original = compile(original, olevel=3)

    if optimized:
        optimized = compile(optimized, olevel=3)

    exe(original, optimized)


def exe(original, optimized=None, **kwargs):
    """
    Checks differences and generates stats and graphs.
    """
    if not optimized:
        return stats(original, **kwargs)

    diff(original, optimized, **kwargs)

    generate_graphs(os.path.splitext(original)[0], [
        stats(original, **kwargs),
        stats(optimized, **kwargs)
    ])

@argument('executable', help='Executable file')
@argument('-q', '--quiet', help="Don't print the stats table", action='store_true')
def stats(executable, quiet=False, executions=1, **kwargs):
    """
    Generates stats with the real time
    """
    name, ext = os.path.splitext(executable)
    filename = "%s.stats" % name

    say("Generating stats for %s..." % executable)
    with open(filename, 'w') as f:
        def _stats(i, *args):
            times = [run(executable, args=args)[2] for _ in xrange(executions)]
            row_id = args[0] if args else i
            row = "%d %.4f\n" % (row_id, sum(times)/executions)
            f.write(row)

            if not quiet:
                sys.stdout.write(row)

        for_each_case(_stats, **kwargs)

    return filename


@argument('original', help='Original executable')
@argument('candidate', help='Candidate executable')
def diff(original, candidate, **kwargs):
    if original == candidate:
        say("Candidate is the original. Skipping diff check...")
        return

    say("Checking differences between %s and %s..." % (original, candidate))

    def _diff(i, *args):
        say("Checking iteration %d with args %s..." % (i, args))

        out1, _, _ = run(original, args=args, output=True)
        out2, _, _ = run(candidate, args=args, output=True)

        file_original = swap_ext(original, 'out')
        file_candidate = swap_ext(candidate, 'out')

        with open(file_original, 'w') as f:
            f.write(out1)

        with open(file_candidate, 'w') as f:
            f.write(out2)

        if subprocess.call(['diff', '-u', file_original, file_candidate]):
            raise RuntimeError("Differences detected!")

        os.remove(file_original)
        os.remove(file_candidate)

    for_each_case(_diff, **kwargs)


def for_each_case(f, arg=None, cases=20, **kwargs):
    if arg is None:
        arg = []

    for i in xrange(1, cases+1):
        args = [eval(a) for a in arg]
        f(i, *args)


def run(exe, args=None, output=False):
    if args is None:
        args = []

    stdout = subprocess.PIPE if output else open('/dev/null')

    cmd = ["./%s" % exe]
    cmd.extend(map(str, args))

    start = time.time()
    process = subprocess.Popen(cmd, stdout=stdout, stderr=subprocess.PIPE)
    out, err = process.communicate()
    elapsed = time.time() - start

    if process.returncode:
        raise RuntimeError("Error when executing %s with args: %s" % (exe, args))

    return out, err, elapsed
