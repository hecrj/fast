"""
A command-line tool to test the optimizations performed to a program
"""
import os
import re
import sys
import subprocess
from reticular import argument


@argument('prog_file', help='File of the program to benchmark')
def benchmark(prog_file):
    """
    Compiles with O0, O1 and O3 and
    """
    if not os.path.isfile(prog_file):
        raise RuntimeError('File not found: %s' % prog_file)

    executables = [
        compile(prog_file),
        compile(prog_file, olevel=1),
        compile(prog_file, olevel=3, native=True)
    ]

    for executable in executables:
        stats(executable)


@argument('executable', help='Executable file')
@argument('-q', '--quiet', help="Don't print the stats table", action='store_true')
def stats(executable, quiet=False, executions=3, decimals_min=500, decimals_max=10000, step=500):
    name, ext = os.path.splitext(executable)

    print "Generating stats for %s..." % executable
    with open("%s.stats" % name, 'w') as f:
        for decimals in xrange(decimals_min, decimals_max+1, step):
            times = [run(executable, decimals) for i in xrange(executions)]
            row = "%d %.4f\n" % (decimals, sum(times)/executions)

            f.write(row)

            if not quiet:
                sys.stdout.write(row)


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
        print 'Removed: %s' % f


def compile(source, compiler='gcc', olevel=0, debug=False, profiling=False, native=False, out=None):
    cmd = [compiler, '-O%d' % olevel]

    if out is None:
        prog_name, ext = os.path.splitext(source)
        out = "%s_o%d.exe" % (prog_name, olevel)

    if debug:
        cmd.append('-g')
    if profiling:
        cmd.append('-pg')
    if native:
        cmd.append('-march=native')

    cmd.extend(['-o', out])
    cmd.append(source)

    print "Compiling %s..." % source
    if subprocess.call(cmd):
        raise RuntimeError("Error when compiling: %s" % source)

    return out


def run(exe, *args):
    cmd = ['time', '-f', 'fast|%e|fast', "./%s" % exe]
    cmd.extend(map(str, args))

    process = subprocess.Popen(cmd, stdout=open("/dev/null"), stderr=subprocess.PIPE)
    out, err = process.communicate()

    elapsed = float(re.search(r'fast\|(\d+\.\d+)\|fast', err).group(1))

    return elapsed
