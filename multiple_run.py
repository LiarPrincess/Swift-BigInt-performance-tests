import os
import time
import shlex
from subprocess import Popen, PIPE

if __name__ == '__main__':
    command = f'python3 __main__.py'
    args = shlex.split(command)

    for i in range(1, 100):
        print(i)
        process = Popen(args, stdout=PIPE, stderr=PIPE)
        process.communicate()
        os.rename('results.md', f'multiple_results/results-{i}.md')
        time.sleep(5 * 60)

