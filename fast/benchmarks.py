from itertools import cycle
import subprocess
from reticular import say
from fast.files import Input, Output, Executable
from fast.utils import gnuplot, normalize_camel_case


class Stats(object):
    POINTS = [1, 12, 2, 3, 4, 5]
    COLORS = [3, 2, 4, 5]

    def __init__(self, name, files, xlabel="Input"):
        self.name = name
        self.files = files
        self.xlabel = xlabel

    def generate_plots(self):
        if subprocess.call(['which', 'gnuplot'], stdout=open('/dev/null', 'w')):
            say("Gnuplot not found. Skipping plot generation...")
            return

        with say("Generating plots for %s..." % self.name):
            self.generate_times()
            self.generate_speedup()

    def generate_times(self):
        say('Generating plot: %s vs Time (s)' % self.xlabel)
        plots = ["'%s' title '%s' pt %d" % (f, f.executable, pt) for f, pt in zip(self.files, cycle(self.POINTS))]
        gnuplot([
            'set ylabel "Time (s)"',
            'set xlabel "%s"' % self.xlabel,
            'set key below',
            "set term pdf color",
            'set output "%s_time.pdf"' % self.name,
            "plot %s" % ', '.join(plots)
        ])

    def generate_speedup(self):
        if len(self.files) < 2:
            return say("Too few stats. Skipping speedup plot...")

        original = self.files[0]
        plots = ["'< paste %s %s' using 1:($2/$4) title '%s/%s' lc %d" % (original, f, original.executable, f.executable,
                                                                          color)
                 for f, color in zip(self.files[1:], cycle(self.COLORS))]
        say("Generating plot: Speedup")
        gnuplot([
            'set ylabel "Speedup"',
            'set xlabel "%s"' % self.xlabel,
            'set key below',
            "set term pdf color",
            'set output "%s_speedup.pdf"' % self.name,
            "plot %s" % ', '.join(plots)
        ])


class BenchmarkBase(object):
    name = None
    target = None
    instances = 20
    executions = 1
    xlabel = "Input"
    stats_class = Stats

    def __init__(self):
        self.original, self.optimized = None, None
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

    def args(self, instance):
        return []

    def input(self, instance):
        raise RuntimeError("input() not implemented in benchmark %s" % self.name)

    def label(self, instance):
        return instance

    def generate_input(self, instance):
        input = Input(benchmark=self.name, label=self.label(instance), args=self.args(instance))

        with input.open('w') as f:
            f.write(self.input(instance))

        return input

    def inputs(self):
        for instance in xrange(1, self.instances+1):
            try:
                self._inputs[instance-1]
            except IndexError:
                self._inputs.append(self.generate_input(instance))

            yield self._inputs[instance-1]

    def full(self, check_diffs=True):
        self.original, self.optimized = self.make()

        with say("Benchmarking %s..." % self.name):
            try:
                if check_diffs:
                    self.check_differences()

                stats = self.generate_stats()
                stats.generate_plots()
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
            files=[self._generate_stats(self.original), self._generate_stats(self.optimized)]
        )

    def _generate_stats(self, executable):
        stats_file = Output(executable=executable, benchmark=self.name, label=self.instances, extension='.stats')

        with say("Generating stats for %s..." % executable), stats_file.open('w') as f:
            say("%s%s" % (self.xlabel.ljust(20), "Time (s)"))
            for input in self.inputs():
                time = executable.average(input, self.executions)
                f.write("%d %.4f\n" % (input.label, time))
                say("%s%.4f" % (str(input.label).ljust(20), time))

        return stats_file


_BENCHMARKS = []


def benchmark(cls):
    cls.name = normalize_camel_case(cls.__name__).replace('_benchmark', '')
    _BENCHMARKS.append(cls)
    return cls


def load_benchmarks():
    try:
        __import__('benchmarks')
        return _BENCHMARKS
    except ImportError:
        raise RuntimeError("No module named benchmarks.py in the current directory.")


def get_benchmark(name):
    benchmarks = load_benchmarks()

    for bmark in benchmarks:
        if bmark.name == name:
            return bmark

    raise RuntimeError("Benchmark with name %s not found" % name)
