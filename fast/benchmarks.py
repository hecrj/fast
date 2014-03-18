import subprocess
from reticular import say
from fast.files import Input


class BenchmarkBase(object):
    name = None
    cases = 20
    executions = 1
    xlabel = "Input"

    def __init__(self, original, optimized):
        self.original = original
        self.optimized = optimized

    def input(self, case):
        raise NotImplementedError

    def label(self, case):
        return case

    def generate_input(self, case):
        input = Input(benchmark=self.name, label=self.label(case))

        with input.open('w') as f:
            f.write(self.input(case))

        return input

    def full(self):
        with say("Benchmarking %s..." % self.name):
            self.diff()

    def diff(self):
        with say("Checking differences between %s and %s..." % (self.original, self.optimized)):
            self.for_each_case(self._diff)

    def _diff(self, input):
        with say("Checking case with label %s..." % input.label):
            out_original, _ = self.original.run(input, save_output=True)
            out_optimized, _ = self.optimized.run(input, save_output=True)

            if subprocess.call(['diff', '-u', out_original.filename, out_optimized.filename]):
                raise RuntimeError("Differences detected!")

            out_original.remove()
            out_optimized.remove()

    def for_each_case(self, function):
        for case in xrange(1, self.cases+1):
            input = self.generate_input(case)
            function(input)
            input.remove()

_BENCHMARKS = {}


def benchmark(cls):
    if not cls.name:
        raise RuntimeError("Some benchmark has not a valid name")

    _BENCHMARKS[cls.name] = cls
    return cls


def load_benchmarks():
    __import__('benchmarks')
    return _BENCHMARKS
