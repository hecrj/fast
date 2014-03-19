import re
import subprocess


def gnuplot(gnuplot_cmd):
    cmd = ['gnuplot', '-e', ';'.join(gnuplot_cmd)]
    subprocess.call(cmd)


# Thanks to http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
def normalize_camel_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
