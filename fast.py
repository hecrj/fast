import sys
import time
import subprocess

def compile(source, compiler='gcc', olevel=0, debug=False,
            profiling=False, native=False, out='_exec'):
    cmd = [compiler, '-O%d'%olevel]

    if debug:
        cmd.append('-g')
    if profiling:
        cmd.append('-pg')
    if native:
        cmd.append('-march=native')

    cmd.extend(['-o', out])
    cmd.append(source)

    ret = subprocess.call(cmd)
    return ret == 0

def run(exe, *args):
    cmd = ["./%s"%exe]
    cmd.extend(map(str, args))

    start = time.time()
    subprocess.call(cmd, stdout=open("/dev/null"))
    elapsed = time.time() - start
    # TODO: Check correctness of output
    return elapsed

def execute(exe, NEXEC, NMIN=500, NMAX=10000, NSTEP=500, statsfile=sys.stdout):
    for decimals in xrange(NMIN, NMAX+1, NSTEP):
        times = []
        for i in xrange(NEXEC):
            times.append(run(exe, decimals))
        statsfile.write("%d %.4f\n" % (decimals, sum(times)/NEXEC))

if __name__ == "__main__":
    compile("pi.c", out="o0.exe")
    compile("pi.c", olevel=1, out="o1.exe")
    compile("pi.c", olevel=3, native=True, out="o3.exe")

    with open('o0.stats', 'w') as f:
        execute("o0.exe", 3, statsfile=f)

    with open('o1.stats', 'w') as f:
        execute("o1.exe", 3, statsfile=f)

    with open('o3.stats', 'w') as f:
        execute("o3.exe", 3, statsfile=f)
