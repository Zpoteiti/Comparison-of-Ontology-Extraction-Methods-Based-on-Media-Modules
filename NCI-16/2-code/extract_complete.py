import os
import csv

def count_lines_with_prefix(file_path, prefixes):
    count = 0
    with open(file_path, 'r') as file:
        for line in file:
            if any(line.startswith(prefix) for prefix in prefixes):
                count += 1
    return count

def main():
    main_folder = "/home/yc/thesis/NCI-16/1-result/1-complete_module/query_sig_10"
    prefixes = ["EquivalentClasses", "SubClassOf"]
    result_file = os.path.join(main_folder, 'result.csv')

    results = []

    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file == "approximate_module.owl":
                file_path = os.path.join(root, file)
                signature_name = os.path.basename(os.path.dirname(file_path))
                size_of_module = count_lines_with_prefix(file_path, prefixes)
                results.append((signature_name, size_of_module))

    # Sort results by signature name, assuming they are numeric
    results.sort(key=lambda x: int(x[0]))

    with open(result_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name of the signature', 'size of the module'])
        writer.writerows(results)

    print(f"Results saved to {result_file}")

if __name__ == "__main__":
    main()
