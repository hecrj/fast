import os
import subprocess
import time


class File(object):
    def __init__(self, filename):
        self.filename = filename

    def open(self, flag):
        return open(self.filename, flag)

    def remove(self):
        os.remove(self.filename)

    def __repr__(self):
        return self.filename


class BenchmarkFile(File):
    def __init__(self, benchmark, label, extension='txt'):
        super(BenchmarkFile, self).__init__("%s_%s.%s" % (benchmark, label, extension))
        self.benchmark = benchmark
        self.label = label


class Input(BenchmarkFile):
    def __init__(self, benchmark, label):
        super(Input, self).__init__(benchmark, label, 'in')


class Output(BenchmarkFile):
    def __init__(self, executable, benchmark, label):
        super(Output, self).__init__(benchmark, label, 'out')
        self.executable = executable
        self.filename = "%s_%s" % (executable, self.filename)


class Executable(File):
    def __init__(self, filename):
        super(Executable, self).__init__(filename)

    def make(self):
        if subprocess.call(['make', self.filename]):
            raise RuntimeError("Make failed")

    def run(self, input, save_output=False):
        stdin = input.open('r')

        output = Output(executable=self.filename, benchmark=input.benchmark, label=input.label)
        stdout = output.open('w') if save_output else open('/dev/null')

        cmd = ["./%s" % self.filename]

        start = time.time()
        returncode = subprocess.call(cmd, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE)
        elapsed = time.time() - start

        if returncode:
            raise RuntimeError("Error when executing %s with input: %s" % (self, input))

        return output, elapsed