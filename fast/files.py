import os
import subprocess
import time


class File(object):
    def __init__(self, filename):
        self.name, self.extension = os.path.splitext(filename)
        self.filename = filename

    def open(self, flag):
        return open(self.filename, flag)

    def remove(self):
        try:
            os.remove(self.filename)
        except OSError:
            pass

    def __repr__(self):
        return self.filename

    def exists(self):
        return os.path.isfile(self.filename)


class BenchmarkFile(File):
    def __init__(self, benchmark, label, extension='.txt'):
        super(BenchmarkFile, self).__init__("%s_%s%s" % (benchmark, label, extension))
        self.benchmark = benchmark
        self.label = label


class Input(BenchmarkFile):
    def __init__(self, benchmark, label, args, extension='.in', constant=False):
        super(Input, self).__init__(benchmark, label, extension)
        self.args = args


class Output(BenchmarkFile):
    def __init__(self, executable, benchmark, label, extension='.out'):
        super(Output, self).__init__(benchmark, label, extension)
        self.executable = executable
        self.filename = "%s_%s_%s" % (executable.name, executable.extension[1:], self.filename)


class Executable(File):
    def __init__(self, filename):
        super(Executable, self).__init__(filename)

    def make(self):
        if subprocess.call(['make', self.filename]):
            raise RuntimeError("Make failed")

    def run(self, input, save_output=False):
        stdin = input.open('r')

        output = Output(executable=self, benchmark=input.benchmark, label=input.label)
        stdout = output.open('w') if save_output else open('/dev/null', 'w')

        cmd = ["./%s" % self.filename]
        cmd.extend([str(arg) for arg in input.args])

        start = time.time()
        returncode = subprocess.call(cmd, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE)
        elapsed = time.time() - start

        if returncode:
            raise RuntimeError("Error when executing %s with input: %s" % (self, input))

        return output, elapsed

    def average(self, input, executions):
        times = [self.run(input, save_output=False)[1] for _ in range(executions)]
        return sum(times)/executions
