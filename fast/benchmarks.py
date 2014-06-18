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
    candidates = None
    diff_script = None
    instances = 20
    executions = 1
    xlabel = "Input"
    stats_class = Stats

    def __init__(self):
        self._inputs = []
        self._original = None
        self._candidates = []

    def make(self):
        if self.target is None:
            raise RuntimeError("No target executable defined in benchmark: %s" % self.name)

        self._original = Executable(self.target)

        if self.candidates is None:
            self.candidates = ["%s_fast%s" % (self._original.name, self._original.extension)]

        try:
            iter(self.candidates)
        except TypeError:
            self.candidates = [self.candidates]

        self._candidates = [Executable(candidate) for candidate in self.candidates]

        with say("Making executables..."):
            self._original.make()

            for candidate in self._candidates:
                candidate.make()

        return self._original, self._candidates

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
        for instance in range(1, self.instances+1):
            try:
                self._inputs[instance-1]
            except IndexError:
                self._inputs.append(self.generate_input(instance))

            yield self._inputs[instance-1]

    def checkpoint(self):
        self.make()

        with say("Checkpoint %s..." % self.name):
            try:
                self._generate_stats(self._original)
            finally:
                self.clean()

    def full(self, check_diffs=True):
        self.make()

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
        if self.diff_script is None:
            for candidate in self._candidates:
                with say("Checking differences between %s and %s..." % (self._original, candidate)):
                    for input in self.inputs():
                        self.diff(input, candidate)
        else:
            with say("Executing differences script: %s" % self.diff_script):
                if subprocess.call(["./%s" % self.diff_script]):
                    raise RuntimeError("Differences detected!")

    def diff(self, input, candidate):
        with say("Checking input %s with args %s..." % (input, input.args)):
            out_original, _ = self._original.run(input, save_output=True)
            out_candidate, _ = candidate.run(input, save_output=True)

            if subprocess.call(['diff', '-u', out_original.filename, out_candidate.filename]):
                raise RuntimeError("Differences detected!")

            out_original.remove()
            out_candidate.remove()

    def generate_stats(self):
        original_stat = Output(self._original, benchmark=self.name, label=self.instances, extension='.stats')

        if not original_stat.exists():
            raise RuntimeError("Original stats file for benchmark %s does not exist. Run checkpoint first." % self.name)

        files = [original_stat]
        files.extend([self._generate_stats(candidate) for candidate in self._candidates])

        return self.stats_class(
            name=self.name,
            xlabel=self.xlabel,
            files=files
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
