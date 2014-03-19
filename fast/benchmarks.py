import subprocess
from reticular import say
from fast.files import Input, Output, Executable
from fast.utils import gnuplot, normalize_camel_case

_BENCHMARKS = {}


class Stats(object):
    def __init__(self, name, original, optimized, xlabel="Input"):
        self.name = name
        self.original = original
        self.optimized = optimized
        self.xlabel = xlabel

    def generate_graphs(self):
        if subprocess.call(['which', 'gnuplot'], stdout=open('/dev/null', 'w')):
            say("Gnuplot not found. Skipping graph generation...")
            return

        with say("Generating graphs for %s..." % self.name):
            self.generate_times()
            self.generate_speedup()

    def generate_times(self):
        say('Generating graph: %s vs Time (s)' % self.xlabel)
        gnuplot([
            'set ylabel "Time (s)"',
            'set xlabel "%s"' % self.xlabel,
            "set term pdf color",
            'set output "%s_time.pdf"' % self.name,
            "plot '%s' title '%s' pt 1, '%s' title '%s' pt 12" % (self.original, self.original.executable,
                                                                  self.optimized, self.optimized.executable)
        ])

    def generate_speedup(self):
        say("Generating graph: Speedup")
        gnuplot([
            'set ylabel "Speedup"',
            'set xlabel "%s"' % self.xlabel,
            "set term pdf color",
            'set output "%s_speedup.pdf"' % self.name,
            "plot '< paste %s %s' using 1:($2/$4) title '%s/%s' lc 3 pt 12" % (self.original, self.optimized,
                                                                               self.original.executable,
                                                                               self.optimized.executable)
        ])


class BenchmarkBase(object):
    name = None
    target = None
    cases = 20
    executions = 1
    xlabel = "Input"
    stats_class = Stats

    def __init__(self):
        self.original, self.optimized = self.make()
        self._inputs = []

    def make(self):
        if self.target is None:
            raise RuntimeError("No target defined in benchmark: %s" % self.name)

        original = Executable("%s" % self.target)
        optimized = Executable("%s_fast%s" % (original.name, original.extension))

        with say("Making executables..."):
            original.make()
            optimized.make()

        return original, optimized

    def args(self, case):
        return []

    def input(self, case):
        raise RuntimeError("input() not implemented in benchmark %s" % self.name)

    def label(self, case):
        return case

    def generate_input(self, case):
        input = Input(benchmark=self.name, label=self.label(case), args=self.args(case),
                      constant=hasattr(self.input, 'constant'))

        if not input.constant or len(self._inputs) == 0:
            with say("Generating input %s..." % input), input.open('w') as f:
                f.write(self.input(case))

        return input

    def inputs(self):
        for case in xrange(1, self.cases+1):
            try:
                self._inputs[case-1]
            except IndexError:
                self._inputs.append(self.generate_input(case))

            yield self._inputs[case-1]

    def full(self, check_diffs=True):
        with say("Benchmarking %s..." % self.name):
            try:
                if check_diffs:
                    self.check_differences()

                stats = self.generate_stats()
                stats.generate_graphs()
            finally:
                self.clean()

    def clean(self):
        for input in self.inputs():
            input.remove()

        self._inputs = []

    def check_differences(self):
        with say("Checking differences between %s and %s..." % (self.original, self.optimized)):
            for input in self.inputs():
                self.diff(input)

    def diff(self, input):
        with say("Checking input %s with args %s..." % (input, input.args)):
            out_original, _ = self.original.run(input, save_output=True)
            out_optimized, _ = self.optimized.run(input, save_output=True)

            if subprocess.call(['diff', '-u', out_original.filename, out_optimized.filename]):
                raise RuntimeError("Differences detected!")

            out_original.remove()
            out_optimized.remove()

    def generate_stats(self):
        return self.stats_class(
            name=self.name,
            xlabel=self.xlabel,
            original=self._generate_stats(self.original),
            optimized=self._generate_stats(self.optimized)
        )

    def _generate_stats(self, executable):
        stats_file = Output(executable=executable, benchmark=self.name, label=self.cases, extension='.stats')

        with say("Generating stats for %s..." % executable), stats_file.open('w') as f:
            for input in self.inputs():
                say("Timing input %s with args %s..." % (input, input.args))
                time = executable.average(input, self.executions)
                row = "%d %.4f\n" % (input.label, time)
                f.write(row)

        return stats_file


def benchmark(cls):
    cls.name = normalize_camel_case(cls.__name__).replace('_benchmark', '')

    _BENCHMARKS[cls.name] = cls
    return cls


def constant(f):
    f.constant = True
    return f


def load_benchmarks():
    try:
        __import__('benchmarks')
        return _BENCHMARKS
    except ImportError:
        raise RuntimeError("No module named benchmarks.py in the current directory.")
