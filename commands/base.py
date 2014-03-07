"""
A command-line tool to test the optimizations performed to a program
"""
import os
import subprocess
from reticular import argument


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
@argument('-c', '--compiler', help='The compiler to use (default %(default)s)', default='gcc')
def compile(source, compiler='gcc', olevel=0, debug=False, profiling=False, native=False, out=None):
    """
    Compiles a source file
    """
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

    print "Compiling %s with %s" % (source, ' '.join(cmd))
    if subprocess.call(cmd, stderr=open('/dev/null')):
        if native:
            print 'warning: native compilation is not supported'
            print 'Retrying without native option...'
            compile(source, compiler=compiler, olevel=olevel, debug=debug, profiling=profiling, native=False, out=out)
        else:
            raise RuntimeError("Error when compiling: %s" % source)

    return out

@argument('source', help='Source file to prepare')
def prepare(source):
    """
    Generates the common used executables for benchmarking
    """
    return [
        compile(source, olevel=0),
        compile(source, olevel=1),
        compile(source, olevel=3, native=True)
    ]
