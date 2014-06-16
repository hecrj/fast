"""
A command-line tool to test the optimizations performed to a program
"""
import os
from reticular import argument, say
from fast.benchmarks import load_benchmarks, get_benchmark


@argument('names', help='Names of the benchmarks to perform', action='append', nargs='?')
def checkpoint(names):
    """
    Creates a checkpoint for the current targets
    """
    benchmarks = load_benchmarks()

    if not any(names):
        names = 'all'

    for benchmark_class in benchmarks:
        if names == 'all' or benchmark_class.name in names:
            bmark = benchmark_class()
            bmark.checkpoint()

    say('Done.')


@argument('--no-diffs', dest='check_diffs', help='Disable difference check', action='store_false')
@argument('names', help='Names of the benchmarks to perform', action='append', nargs='?')
def benchmark(names, check_diffs):
    """
    Performs benchmarks to the specified program
    """
    benchmarks = load_benchmarks()

    if not any(names):
        names = 'all'

    for benchmark_class in benchmarks:
        if names == 'all' or benchmark_class.name in names:
            bmark = benchmark_class()
            bmark.full(check_diffs=check_diffs)

    say('Done.')


@argument('instances', help='Instances of the inputs to generate', action='append', type=int, nargs='?')
@argument('name', help='Name of the benchmark to generate input')
def generate(name, instances):
    if not any(instances):
        instances = [1]

    bmark = get_benchmark(name)()

    for instance in instances:
        with say("Generating input for instance %d..." % instance):
            input = bmark.generate_input(instance)
            say("Generated: %s" % input)


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
