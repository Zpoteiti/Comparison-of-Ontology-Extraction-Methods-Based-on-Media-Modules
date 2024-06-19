import os
import csv

def extract_information(file_path):
    parts = os.path.splitext(os.path.basename(file_path))[0].split('-')
    signature = parts[0]
    iteration = parts[1]

    first_module_size = None
    union_module_size = set()
    num_minimal_modules = None

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "The size of a minimal module:" in line:
                first_module_size = int(line.split(":")[1].strip())
            elif line.startswith("SubClassOf") or line.startswith("EquivalentClasses"):
                union_module_size.add(line.strip())
            elif "Number of minimal modules:" in line:
                num_minimal_modules = int(line.split(":")[1].strip())

    return {
        'Signature': signature,
        'Iteration': iteration,
        'First Minimal Module Size': first_module_size,
        'Union of All Module Size': len(union_module_size),
        'Number of Minimal Modules': num_minimal_modules
    }

def main(folder_path, total_signatures, iterations_per_signature):
    result_data = []
    for signature in range(total_signatures):
        na_recorded = False
        for iteration in range(1, iterations_per_signature + 1):
            file_path = os.path.join(folder_path, f"{signature}-{iteration}.txt")
            if os.path.exists(file_path):
                result_data.append(extract_information(file_path))
            elif not na_recorded:
                result_data.append({
                    'Signature': signature,
                    'Iteration': iteration,
                    'First Minimal Module Size': 'NA',
                    'Union of All Module Size': 'NA',
                    'Number of Minimal Modules': 'NA'
                })
                na_recorded = True

    result_csv_path = os.path.join(folder_path, 'result.csv')
    with open(result_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Signature', 'Iteration', 'First Minimal Module Size', 'Union of All Module Size', 'Number of Minimal Modules']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in result_data:
            writer.writerow(data)

    print(f"Results have been written to {result_csv_path}")

if __name__ == "__main__":
    folder_path = "/home/yc/thesis/NCI-16/1-result/2-final_zoom/sig_50_10"
    total_signatures = 100  # Adjust as needed
    iterations_per_signature = 10  # Assuming 10 iterations per signature
    main(folder_path, total_signatures, iterations_per_signature)
