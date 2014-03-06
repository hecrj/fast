"""
A command-line tool to test the optimizations performed to a program
"""
import os
import subprocess
from reticular import argument
from benchmark import stats


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


@argument('source', help='Source file to compile')
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
