"""
A command-line tool to test the optimizations performed to a program
"""
import os
from reticular import argument, say, command
from fast.benchmarks import load_benchmarks


@command
def benchmark():
    """
    Performs benchmarks to the specified program
    """
    benchmarks = load_benchmarks()

    for benchmark_class in benchmarks.values():
        bmark = benchmark_class()
        bmark.full()

    say('Done.')


@argument('-s', '--stats', help='Clean .stats files', action='store_true')
def clean(stats):
    """
    Cleans fast-generated files of the current directory
    """
    ends = ['.exe']

    if stats:
        ends.append('.stats')

    remove_files = (f for f in os.listdir('.') if os.path.splitext(f)[-1] in ends)

    for f in remove_files:
        os.remove(f)
        say('Removed: %s' % f)
