# coding=utf-8
# fast setup.py
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="fast-cli",
    packages=["fast", "fast.commands"],
    version="0.0.8",
    description="Command-line tool to test the optimizations performed to a program",
    author="Héctor Ramón Jiménez, and Alvaro Espuña Buxo",
    author_email="hector0193@gmail.com",
    url="https://github.com/hacs/fast",
    keywords=["command", "line", "tool"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description="""\
fast is a command-line tool to test the optimizations performed to a program.
""",
    install_requires=[
        'reticular == 0.0.10'
    ],
    entry_points={
        'console_scripts': ['fast = fast.base:console']
    }
)
