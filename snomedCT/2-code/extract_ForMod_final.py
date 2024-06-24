import os
import csv
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_information(file_path):
    signature = os.path.splitext(os.path.basename(file_path))[0]
    average_module_size = None
    union_module_size = set()
    num_minimal_modules = None
    total_size = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "The size of a minimal module:" in line:
                total_size += int(line.split(":")[1].strip())
            elif line.startswith("SubClassOf") or line.startswith("EquivalentClasses"):
                union_module_size.add(line.strip())
            elif "Number of minimal modules:" in line:
                num_minimal_modules = int(line.split(":")[1].strip())

    if num_minimal_modules and num_minimal_modules > 0:
        average_module_size = total_size / num_minimal_modules
    else:
        average_module_size = 'NA'

    return {
        'Signature': signature,
        'Average Minimal Module Size': average_module_size,
        'Union of All Module Size': len(union_module_size),
        'Number of Minimal Modules': num_minimal_modules if num_minimal_modules is not None else 'NA'
    }

def main(folder_path, total_files):
    result_data = []
    for i in range(total_files):
        file_path = os.path.join(folder_path, f"{i}.txt")
        if os.path.exists(file_path):
            logger.info(f"Processing file: {file_path}")
            result_data.append(extract_information(file_path))
        else:
            logger.warning(f"File not found: {file_path}")
            result_data.append({
                'Signature': i,
                'Average Minimal Module Size': 'NA',
                'Union of All Module Size': 'NA',
                'Number of Minimal Modules': 'NA'
            })

    result_csv_path = os.path.join(folder_path, 'result.csv')
    with open(result_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Signature', 'Average Minimal Module Size', 'Union of All Module Size', 'Number of Minimal Modules']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in result_data:
            writer.writerow(data)

if __name__ == "__main__":
    folder_path = "/home/yc/thesis-main/snomedCT/1_result/2-final_mex"
    total_files = 1000
    main(folder_path, total_files)
