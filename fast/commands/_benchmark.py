"""
Benchmark commands
"""
import os
import subprocess
import sys
from reticular import argument, global_arg, say
from fast.utils import generate_graphs, for_each_case, run, swap_ext

ARGUMENTS = [
    global_arg('-c', '--cases', help='Number of cases (default: %(default)s)', default=20, type=int),
    global_arg('-e', '--executions', help='Number of executions per case (default: %(default)s)', default=1)
]





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
