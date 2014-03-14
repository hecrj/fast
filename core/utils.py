import os
import subprocess
from reticular import say


def gnuplot(gnuplot_cmd):
    cmd = ['gnuplot', '-e', ';'.join(gnuplot_cmd)]
    subprocess.call(cmd)


def generate_graphs(name, files):
    if subprocess.call(['which', 'gnuplot']):
        say("Gnuplot not found. Skipping graph generation...")
        return

    # First graph: Time - Input
    gnuplot([
        'set ylabel "Time (s)"',
        'set xlabel "Input"',
        "set term pdf color",
        'set output "%s_a.pdf"' % name,
        "plot %s" % ', '.join('"{0}"'.format(name) for name in files)
    ])


def swap_ext(filename, new_ext):
    return "%s.%s" % (os.path.splitext(filename)[0], new_ext)
