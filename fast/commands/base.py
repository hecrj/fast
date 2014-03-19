"""
A command-line tool to test the optimizations performed to a program
"""
import os
from reticular import argument, say, command
from fast.benchmarks import load_benchmarks


@argument('--no-diffs', dest='check_diffs', help='Disable difference check', action='store_false')
@argument('names', help='Names of the benchmarks to perform', action='append', nargs='?')
def benchmark(names, check_diffs):
    """
    Performs benchmarks to the specified program
    """
    benchmarks = load_benchmarks()

    if not any(names):
        names = 'all'

    for name, benchmark_class in benchmarks.iteritems():
        if names == 'all' or name in names:
            bmark = benchmark_class()
            bmark.full(check_diffs=check_diffs)

    say('Done.')


@argument('-s', '--stats', help='Clean .stats files', action='store_true')
def clean(stats):
    """
    Cleans fast-generated files of the current directory
    """
    ends = ['.in', '.out']

    if stats:
        ends.append('.stats')

    remove_files = (f for f in os.listdir('.') if os.path.splitext(f)[-1] in ends)

    for f in remove_files:
        os.remove(f)
        say('Removed: %s' % f)
