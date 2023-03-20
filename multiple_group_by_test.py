import os

CURRENT_DIR = os.getcwd()
INPUT_DIR = os.path.join(CURRENT_DIR, 'multiple_results')
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'multiple_grouped_by_test')


def parse_result_file(path: str) -> dict[str, str]:
    current_test_name = ''
    current_content = ''
    test_name_to_content = {}

    def append_current_test():
        nonlocal current_test_name, current_content

        if current_test_name and current_content:
            test_name_to_content[current_test_name] = current_content
            current_test_name = ''
            current_content = ''

    with open(path, 'r') as f:
        for line in f.readlines():
            line = line.strip()

            if not line:
                pass
            elif line.startswith('#'):
                append_current_test()
                current_test_name = line[1:].strip()
            else:
                # Separate pi table from main table
                is_python_pi_table = line.startswith('Python')
                if is_python_pi_table:
                    current_content += '\n'

                current_content += line
                current_content += '\n'

                if is_python_pi_table:
                    current_content += '\n'

    append_current_test()
    return test_name_to_content


def main():
    file_names = os.listdir(INPUT_DIR)
    file_names.sort()
    test_name_to_tables: dict[str, list[str]] = {}

    for name in file_names:
        if name.startswith('.'):
            continue

        path = os.path.join(INPUT_DIR, name)
        test_name_to_content = parse_result_file(path)

        for test_name, content in test_name_to_content.items():
            if test_name not in test_name_to_tables:
                test_name_to_tables[test_name] = []

            test_name_to_tables[test_name].append(content)

    for test_index, (test_name, tables) in enumerate(test_name_to_tables.items()):
        file_name_test_name = test_name.replace(',', '').replace(' ', '_')
        file_name = f'{test_index}_{file_name_test_name}.md'
        file_path = os.path.join(OUTPUT_DIR, file_name)

        with open(file_path, 'w') as f:
            for index, content in enumerate(tables):
                f.write('# ')
                f.write(test_name)
                f.write(' - ')
                f.write(str(index))
                f.write('\n')
                f.write(content)
                f.write('\n')


if __name__ == '__main__':
    main()
