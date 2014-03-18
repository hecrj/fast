"""
A command-line tool to test the optimizations performed to a program
"""
import os
from reticular import argument, say, global_arg, command
from fast.benchmarks import load_benchmarks
from fast.files import Executable


ARGUMENTS = (
    global_arg('name', help='Program name to benchmark'),
)


@command
def make(name):
    """
    Use Makefile to make program executables
    """
    original = Executable("%s.3" % name)
    optimized = Executable("%s_fast.3" % name)

    say("Making executables...")
    original.make()
    optimized.make()

    return original, optimized


@command
def benchmark(name):
    """
    Performs benchmarks to the specified program
    """
    original, optimized = make(name)
    benchmarks = load_benchmarks()

    for benchmark_class in benchmarks.values():
        bmark = benchmark_class(original=original, optimized=optimized)
        bmark.full()


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
