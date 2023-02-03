import re
import sys
import math
import shlex
import timeit
import os.path
from typing import List, Optional
from subprocess import Popen, PIPE
from dataclasses import dataclass
from collections import defaultdict

# You only need to configure those PATHs below.
# You may also want to modify 'IMPLEMENTATIONS' to include only the ones you want.

# Path to: https://github.com/LiarPrincess/swift-numerics/tree/13-Performance
# Branch: 13-Performance
SWIFT_NUMERICS_PATH = '/mnt/Storage/Programming/swift-numerics'
# Path to: https://github.com/LiarPrincess/Violet/tree/swift-numerics
# Branch: swift-numerics
VIOLET_PATH = '/mnt/Storage/Programming/Violet'
# Path to: https://github.com/LiarPrincess/BigInt/tree/Performance-tests
# Branch: Performance-tests
ATTASWIFT_PATH = '/mnt/Storage/Programming/attaswift-bigint'

OPTIONS_DEBUG = []
OPTIONS_RELEASE = [
    '--configuration', 'release',
    '-Xswiftc', '-gnone',  # Don't emit debug info
    '-Xswiftc', '-O',  # Compile with optimizations
]
OPTIONS_UNCHECKED = [
    '--configuration', 'release',
    '-Xswiftc', '-gnone',  # Don't emit debug info
    '-Xswiftc', '-Ounchecked',  # Compile with optimizations and remove runtime safety checks
]

PLATFORM = \
    '🐧' if sys.platform == 'linux' else \
    '🍎' if sys.platform == 'darwin' else \
    '🪟'

INCLUDE_STANDARD_DEVIATION = False


# =======================
# === Implementations ===
# =======================

@dataclass
class Implementation:
    name: str
    path: str
    test_target_name: str  # Replace '-' with '_', otherwise 'swift test' fails
    test_file_relative_path: str
    options: List[str]


SWIFT_NUMERICS = Implementation(
    name=f'{PLATFORM} swift_numerics',
    path=SWIFT_NUMERICS_PATH,
    test_target_name='BigIntTests',
    test_file_relative_path='Tests/BigIntTests/Performance/PerformanceTests.generated.swift',
    options=OPTIONS_RELEASE
)

VIOLET = Implementation(
    name=f'{PLATFORM} Violet',
    path=VIOLET_PATH,
    test_target_name='BigIntTests_swift_numerics',
    test_file_relative_path='Tests/BigIntTests-swift-numerics/Performance/PerformanceTests.generated.swift',
    options=OPTIONS_RELEASE
)

ATTASWIFT = Implementation(
    name=f'{PLATFORM} attaswift',
    path=ATTASWIFT_PATH,
    test_target_name='PerformanceTests',
    test_file_relative_path='Tests/Performance/PerformanceTests.generated.swift',
    options=OPTIONS_RELEASE
)

# 1st entry is a reference implementation,
# all of the others will be compared with it.
IMPLEMENTATIONS = (
    SWIFT_NUMERICS,
    VIOLET,
    ATTASWIFT,
)


# =================
# === Test file ===
# =================

@dataclass
class TestFile:
    path: str
    class_name: str
    test_names: List[str]


def read_test_file(i: Implementation) -> TestFile:
    class_name = None
    test_names = []
    path = os.path.join(i.path, i.test_file_relative_path)

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith('class') and 'XCTestCase' in line:
                if class_name is not None:
                    raise ValueError(f'Multiple test classes in: {path}')

                try:
                    colon_index = line.index(':')
                    class_name = line[5:colon_index].strip()
                except ValueError:
                    raise ValueError(f"Unable to parse '{line}' test class name in: {path}")

            elif line.startswith('func test'):
                try:
                    brace_index = line.index('(')
                    name = line[4:brace_index].strip()
                    test_names.append(name)
                except ValueError:
                    raise ValueError(f"Unable to parse '{line}' test name in: {path}")

    if class_name is None:
        raise ValueError(f'Unable to find test class name in: {path}')

    if not test_names:
        raise ValueError(f'Unable to find tests in: {path}')

    return TestFile(path, class_name, test_names)


# ================
# === Run test ===
# ================

@dataclass
class TestResult:
    average: float
    standard_deviation: float
    values: List[float]


TEST_RESULT_LINE_REGEX = re.compile('average: (\\d+\\.\\d+(?:e-\\d+)?).*values: \\[(.*)\\]', re.IGNORECASE)


def run_test_case(i: Implementation, test_file: TestFile, test_name: str) -> TestResult:
    command = (
        'swift',
        'test',
        '--package-path', f'"{i.path}"',
        '--filter', f'{i.test_target_name}.{test_file.class_name}/{test_name}',
        '--enable-test-discovery',
        '-Xswiftc', '-DPERFORMANCE_TEST',
        *i.options
    )

    command = ' '.join(command)
    args = shlex.split(command)
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return_code = process.poll()

    stdout = str(stdout, 'utf-8')
    stderr = str(stderr, 'utf-8')

    if return_code != 0:
        print('--- stdout ---')
        print(stdout)
        print('--- stderr ---')
        print(stderr)
        raise ValueError(f"Return code {return_code} for: {test_file.class_name}.{test_name}")

    # Test results are in:
    # - 'stdout' on Linux
    # - 'stderr' on mac
    out = stdout + '\n' + stderr

    for line in out.splitlines():
        r = TEST_RESULT_LINE_REGEX.search(line)
        if r is None:
            continue

        average_group = r.group(1)
        average = float(average_group)

        values_group = r.group(2)
        values: list[float] = []
        standard_deviation = 0.0

        for s in values_group.split(','):
            s = s.replace('seconds', '').strip()
            f = float(s)
            standard_deviation += pow(f - average, 2)
            values.append(f)

        standard_deviation /= len(values)
        standard_deviation = math.sqrt(standard_deviation)
        return TestResult(average, standard_deviation, values)

    print('--- stdout ---')
    print(stdout)
    print('--- stderr ---')
    print(stderr)
    raise ValueError(f"Unable to stdout for: {test_file.class_name}.{test_name}")


# ============
# === Main ===
# ============

def cell_value(average: float, standard_deviation: float, first: Optional[float]) -> str:
    value = str(average)

    if INCLUDE_STANDARD_DEVIATION and math.isfinite(standard_deviation):
        value += f' [{standard_deviation:.4}σ]'

    if first is None:
        return value

    to_first = 0.0 if average == 0 else first / average
    value += f' ({to_first:.3}x)'

    return \
        f'<span style="color:#39a275">{value}</span>' if to_first > 1.1 else \
        f'<span style="color:#df1c44">{value}</span>' if to_first < 0.9 else \
        value


def main():
    assert len(IMPLEMENTATIONS), 'No implementations to test?'
    test_name_to_results: defaultdict[str, list[TestResult]] = defaultdict(lambda: [])
    test_start_time = timeit.default_timer()

    for i in IMPLEMENTATIONS:
        print(i.name)
        test_file = read_test_file(i)
        t_start_time = timeit.default_timer()

        for test_name in test_file.test_names:
            # if 'string' in test_name or 'unary' in test_name:
            print(f'  {test_name}')
            r = run_test_case(i, test_file, test_name)
            test_name_to_results[test_name].append(r)

        i_end_time = timeit.default_timer()
        print(f'  Total: {int(i_end_time - t_start_time)}s (includes compilation time)')

    print('Writing results file…')
    with open('results.md', 'w') as f:
        names_line = '| |'
        separator_line = '|-|'

        for i in IMPLEMENTATIONS:
            names_line += i.name + '|'
            separator_line += (len(i.name) * '-') + '|'

        def write_results(filters: List[str]):
            f.write('# ' + ', '.join(filters).replace('_', '') + '\n')
            f.write('\n')
            f.write(names_line + '\n')
            f.write(separator_line + '\n')

            totals = [0.0] * len(IMPLEMENTATIONS)

            for test_name in test_name_to_results:
                is_accepted = any(map(lambda f: f in test_name, filters))
                if is_accepted:
                    line = '|' + test_name + '|'
                    results = test_name_to_results[test_name]
                    assert len(results) == len(IMPLEMENTATIONS), f"'{test_name}' was not run in all implementations?"

                    for (index, r) in enumerate(results):
                        first = None if index == 0 else results[0].average
                        value = cell_value(r.average, r.standard_deviation, first)
                        line += value + '|'
                        totals[index] += r.average

                    f.write(line + '\n')

            total_line = '|TOTAL|'
            for index, t in enumerate(totals):
                first = None if index == 0 else totals[0]
                value = cell_value(t, float('nan'), first)
                total_line += value + '|'

            f.write(total_line + '\n')
            f.write('\n')

        write_results(['_string_'])
        write_results(['_unary_'])
        write_results(['_add_', '_sub_'])
        write_results(['_mul_', '_div_', '_mod_'])
        write_results(['_and_', '_or_', '_xor_'])
        write_results(['_shift'])

    test_end_time = timeit.default_timer()
    print(f'Total: {int(test_end_time - test_start_time)}s')


if __name__ == '__main__':
    main()
