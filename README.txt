fast
============
A command-line tool to test the optimizations performed to a program.
With `fast` you can perform benchmarks to different executables in a really easy way!


Installation
------------
```
$ pip install fast-cli
```

`fast` is still in a very early stage of development. This means that lots of changes are likely to occur, and your old benchmarks could need to be changed in order to work with the new versions.


Usage
------------
`fast` tries to load a Python module `benchmarks.py` located in the current working directory. In this module you need to define the different benchmarks that you want to perform to your executables!

Here is how you can define benchmarks in `benchmarks.py`:

```python
from fast.benchmarks import benchmark, BenchmarkBase

@benchmark
class DocUsageBenchmark(BenchmarkBase):
    # The original executable from which to compare the optimizations
    target = 'my_executable'

    # A list of optimized executables
    # default: self.target but with `_fast` appended before its extension
    candidates = ('my_executable_v2',)

    # Number of instances that you want for your benchmark samples
    # default: 20
    instances = 20

    # Number of executions per instance
    # The average time is taken as the total time of the instance
    # default: 1
    executions = 2

    # Main label for the generated inputs
    # default: "Input"
    xlabel = "Number of as"

    def args(self, instnace):
        """
        Arguments that should be provided to the executables for the given instance
        """
        return []

    def input(self, instance):
        """
        Input that should be provided to the executables for the given instance
        """
        return "a" * instance

    def label(self, instance):
        """
        Label for the given instance
        """
        return instance
```

The command `benchmark` will run the benchmarks in `benchmarks.py` that are decorated with `@benchmark`, also it accepts the names of the benchmarks as arguments. The name of one benchmark is its class name but replacing CamelCase with underscores. For example, you could be able to run the previous benchmark doing: `fast benchmark doc_usage`

To make the executables, `fast` invokes `make name_of_the_executable` before performing each benchmark. Therefore, you need to have a `Makefile` with the correct rules to generate your executables.


Example
------------
Let's see how we can use `fast` in a real-world example.

Suppose that we want to optimize a program named `swap` that reads the input in pairs of bytes and writes them in the output in reverse order. If the number of bytes of the input file is odd, then the last byte it's left in the same position.

We could write `benchmarks.py` as follows:

```python
from fast.benchmarks import benchmark, BenchmarkBase

@benchmark
class DataSizeBenchmark(BenchmarkBase):
    target = 'swap'
    instances =  20
    executions = 3
    xlabel = "Data size (Mbytes)"

    def input(self, instance):
        return "abc" * ((instance * 1024 * 1024) / 3)

    def label(self, instance):
        return instance
```

We define a benchmark that is going to increase the input size from 1 Mbyte to 20 Mbytes targeting the `swap` executable. We have not defined any candidate, so by default `fast` is going to try to make a `swap_fast` executable to perform the benchmark.

Now, we perform the benchmark:


```
hector@Ubi:~/example/swap$ fast benchmark
Making executables...
make: `swap' is up to date.
gcc  swap_fast.c -o swap_fast
Benchmarking data_size...
  Checking differences between swap and swap_fast...
    Checking input data_size_1.in with args []...
    Checking input data_size_2.in with args []...
    Checking input data_size_3.in with args []...
    [...]
    Checking input data_size_20.in with args []...
  Generating stats for swap...
    Data size (Mbytes)  Time (s)
    1                   0.2670
    2                   0.5348
    3                   0.7982
    [...]
    20                  5.4169
  Generating stats for swap_fast...
    Data size (Mbytes)  Time (s)
    1                   0.0023
    2                   0.0024
    3                   0.0046
    [...]
    20                  0.0192
  Generating plots for data_size...
    Generating plot: Data size (Mbytes) vs Time (s)
    Generating plot: Speedup
Done.
```

`fast` creates `.stats` files for each executable of the benchmark and two plots in `.pdf`: one that shows the Input vs Time of the target and the candidates, and another that shows the Input vs Speedup.


### DataSizeBenchmark

![Data size (Mbytes) - Time (s)](http://i.imgur.com/5Fnt6wG.png)
![Data size (Mbytes) - Speedup](http://i.imgur.com/tkEkvwF.png)

Our optimization worked. We got huge speedups for all the inputs!
