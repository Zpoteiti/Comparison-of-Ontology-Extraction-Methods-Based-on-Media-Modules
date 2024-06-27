import os
import csv

def extract_information(file_path):
    signature = os.path.splitext(os.path.basename(file_path))[0]
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
        'First Minimal Module Size': first_module_size,
        'Union of All Module Size': len(union_module_size),
        'Number of Minimal Modules': num_minimal_modules
    }

def main(folder_path):
    result_data = []
    for i in range(100):
        file_path = os.path.join(folder_path, f"{i}.txt")
        if os.path.exists(file_path):
            result_data.append(extract_information(file_path))
        else:
            result_data.append({
                'Signature': i,
                'First Minimal Module Size': 'NA',
                'Union of All Module Size': 'NA',
                'Number of Minimal Modules': 'NA'
            })

    result_csv_path = os.path.join(folder_path, 'result.csv')
    with open(result_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Signature', 'First Minimal Module Size', 'Union of All Module Size', 'Number of Minimal Modules']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in result_data:
            writer.writerow(data)

if __name__ == "__main__":
    folder_path = "/home/yc/thesis/NCI-16/1-Result/2-AllMinMods/sig_50_1"
    main(folder_path)
