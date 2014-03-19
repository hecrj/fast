import subprocess
from reticular import say
from fast.files import Input, Output, Executable
from fast.utils import gnuplot

_BENCHMARKS = {}


class Stats(object):
    def __init__(self, name, original, optimized, input_label="Input"):
        self.name = name
        self.original = original
        self.optimized = optimized
        self.input_label = input_label

    def generate_graphs(self):
        if subprocess.call(['which', 'gnuplot'], stdout=open('/dev/null', 'w')):
            say("Gnuplot not found. Skipping graph generation...")
            return

        with say("Generating graphs for %s..." % self.name):
            self.generate_times()
            self.generate_speedup()

    def generate_times(self):
        say('Generating graph: %s vs Time (s)' % self.input_label)
        gnuplot([
            'set ylabel "Time (s)"',
            'set xlabel "%s"' % self.input_label,
            "set term pdf color",
            'set output "%s_time.pdf"' % self.name,
            "plot '%s' title '%s' pt 1, '%s' title '%s' pt 12" % (self.original, self.original.executable,
                                                                  self.optimized, self.optimized.executable)
        ])

    def generate_speedup(self):
        say("Generating graph: Speedup")
        gnuplot([
            'set ylabel "Speedup"',
            'set xlabel "%s"' % self.input_label,
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
    input_label = "Input"
    stats_class = Stats

    def __init__(self):
        self.original, self.optimized = self.make()

    def make(self):
        if self.target is None:
            raise RuntimeError("No target defined in benchmark: %s" % self.name)

        original = Executable("%s" % self.target)
        optimized = Executable("%s_fast%s" % (original.name, original.extension))

        with say("Making executables..."):
            original.make()
            optimized.make()

        return original, optimized

    def input(self, case):
        raise NotImplementedError

    def label(self, case):
        return case

    def generate_input(self, case):
        input = Input(benchmark=self.name, label=self.label(case))

        with input.open('w') as f:
            f.write(self.input(case))

        return input

    def inputs(self):
        for case in xrange(1, self.cases + 1):
            input = self.generate_input(case)
            yield input
            input.remove()

    def full(self):
        with say("Benchmarking %s..." % self.name):
            self.check_differences()
            stats = self.generate_stats()
            stats.generate_graphs()

    def check_differences(self):
        with say("Checking differences between %s and %s..." % (self.original, self.optimized)):
            for input in self.inputs():
                self.diff(input)

    def diff(self, input):
        with say("Checking input with label %s..." % input.label):
            out_original, _ = self.original.run(input, save_output=True)
            out_optimized, _ = self.optimized.run(input, save_output=True)

            if subprocess.call(['diff', '-u', out_original.filename, out_optimized.filename]):
                raise RuntimeError("Differences detected!")

            out_original.remove()
            out_optimized.remove()

    def generate_stats(self):
        return self.stats_class(
            name=self.name,
            input_label=self.input_label,
            original=self._generate_stats(self.original),
            optimized=self._generate_stats(self.optimized)
        )

    def _generate_stats(self, executable):
        stats_file = Output(executable=executable, benchmark=self.name, label=self.cases, extension='.stats')

        with say("Generating stats for %s..." % executable), stats_file.open('w') as f:
            for input in self.inputs():
                time = executable.average(input, self.executions)
                row = "%d %.4f\n" % (input.label, time)
                f.write(row)

        return stats_file


def benchmark(cls):
    if not cls.name:
        raise RuntimeError("Some benchmark has not a valid name")

    _BENCHMARKS[cls.name] = cls
    return cls


def load_benchmarks():
    try:
        __import__('benchmarks')
        return _BENCHMARKS
    except ImportError:
        raise RuntimeError("No module named benchmarks.py in the current directory.")
