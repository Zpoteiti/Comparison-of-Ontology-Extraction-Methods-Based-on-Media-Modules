import os
import csv
from pathlib import Path

def count_lines_with_prefix(file_path, prefixes):
    """Count the number of lines in the file that start with any of the given prefixes."""
    count = 0
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if any(line.startswith(prefix) for prefix in prefixes):
                    count += 1
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
    return count

def main():
    main_folder = Path("/home/yc/thesis/snomedCT/1_result/1-complete_module")
    prefixes = ["EquivalentClasses", "SubClassOf"]
    result_file = main_folder / 'result.csv'

    results = []

    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file == "approximate_module.owl":
                file_path = Path(root) / file
                signature_name = Path(root).name
                size_of_module = count_lines_with_prefix(file_path, prefixes)
                results.append((signature_name, size_of_module))

    # Sort results by signature name, assuming they are numeric
    results.sort(key=lambda x: int(x[0]))

    try:
        with result_file.open('w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['name of the signature', 'size of the module'])
            writer.writerows(results)
        print(f"Results saved to {result_file}")
    except IOError as e:
        print(f"Error writing to file {result_file}: {e}")

if __name__ == "__main__":
    main()
