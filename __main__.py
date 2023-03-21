from io import TextIOWrapper


def raw_input_group_by_operation():
    with open('operations.txt', 'r') as f:
        inits = []
        adds = []
        subs = []
        muls = []
        divs = []
        greater_thans = []

        for line in f:
            line = line.strip()

            if not line or ':' in line:  # pi digits
                continue

            if line.startswith('init'):
                inits.append(line + '\n')
            elif line.startswith('add'):
                adds.append(line + '\n')
            elif line.startswith('sub'):
                subs.append(line + '\n')
            elif line.startswith('mul'):
                muls.append(line + '\n')
            elif line.startswith('div'):
                divs.append(line + '\n')
            elif line.startswith('greater_than'):
                greater_thans.append(line + '\n')
            else:
                raise ValueError(f"Unknown operation '{line}'")

    with open('init.txt', 'w') as f:
        f.writelines(inits)
    with open('add.txt', 'w') as f:
        f.writelines(adds)
    with open('sub.txt', 'w') as f:
        f.writelines(subs)
    with open('mul.txt', 'w') as f:
        f.writelines(muls)
    with open('div.txt', 'w') as f:
        f.writelines(divs)
    with open('greater_than.txt', 'w') as f:
        f.writelines(greater_thans)


ROW_GROUP = 200
COL_GROUP = 200
CAPACITY = 5000


def print_table(out: TextIOWrapper, file: str):
    lhs_max = 0
    rhs_max = 0
    lhs_to_rhs_to_count: list[list[int]] = [([0] * CAPACITY) for _ in range(0, CAPACITY)]

    with open(file, 'r') as f:
        for line in f:
            line = line.strip()

            if line:
                op, lhs_count, rhs_count = line.split('|')
                lhs_count = int(lhs_count)
                rhs_count = int(rhs_count)

                lhs_max = max(lhs_max, lhs_count)
                rhs_max = max(rhs_max, rhs_count)
                lhs_to_rhs_to_count[lhs_count][rhs_count] += 1

    row_count = lhs_max // ROW_GROUP + 1
    column_count = rhs_max // COL_GROUP + 1

    # Header
    out.write('|lhs/rhs|')
    for i in range(0, column_count):
        start = i * COL_GROUP
        end = start + COL_GROUP
        out.write(f'{start}|')
    out.write('\n')
    out.write('|-|')
    for i in range(0, column_count):
        out.write(f'-|')
    out.write('\n')

    # Rows
    for l in range(0, row_count):
        lhs_start = l * ROW_GROUP
        lhs_end = lhs_start + ROW_GROUP
        out.write(f'|{lhs_start}|')

        for r in range(0, column_count):
            rhs_start = r * COL_GROUP
            rhs_end = rhs_start + COL_GROUP

            count = 0
            for ll in range(lhs_start, lhs_end):
                for rr in range(rhs_start, rhs_end):
                    count += lhs_to_rhs_to_count[ll][rr]

            out.write(f'{count}|')
        out.write('\n')

    out.write('\n')
    out.write('\n')


def main():
    raw_input_group_by_operation()

    with open(f'result.md', 'w') as f:
        def print_header(s: str):
            f.write('# ')
            f.write(s)
            f.write('\n\n')

        f.write(f'''\
- row - number of words (`UInt64` in magnitude) in `lhs`
- column - number of words in `rhs`
- value - number of operations where:
  - `lhs` word count was between `row` and `row+{ROW_GROUP}`
  - `rhs` word count was between `column` and `column+{COL_GROUP}`

''')

        print_header('Add')
        print_table(f, 'add.txt')

        print_header('Sub')
        print_table(f, 'sub.txt')

        print_header('Mul')
        f.write('`rhs` is always a single word\n\n')
        print_table(f, 'mul.txt')

        print_header('Div')
        print_table(f, 'div.txt')

        print_header('Greater than (>)')
        print_table(f, 'greater_than.txt')


if __name__ == '__main__':
    main()
