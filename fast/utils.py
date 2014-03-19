import subprocess


def gnuplot(gnuplot_cmd):
    cmd = ['gnuplot', '-e', ';'.join(gnuplot_cmd)]
    subprocess.call(cmd)
