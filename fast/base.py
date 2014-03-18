import reticular
import sys


def console():
    # Add working directory to system path
    sys.path.append('.')

    message = '''________             _____
___  __/_____ _________  /_
__  /_ _  __ `/_  ___/  __/
_  __/ / /_/ /_(__  )/ /_
/_/    \__,_/ /____/ \__/

Welcome! Use -h or --help to see command help.'''

    reticular.CLI(
        name='fast',
        version='0.0.1',
        message=message
    ).run()
