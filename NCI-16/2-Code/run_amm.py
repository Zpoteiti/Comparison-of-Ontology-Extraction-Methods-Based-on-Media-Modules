import os
import csv
import subprocess
import time
import signal
import logging

# Constants for AllMinMods
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/NCI-16/External_program&data/blackbox.jar"
ONTOLOGY_PATH = "/home/yc/thesis/NCI-16/External_program&data/nci-16.owl"
SIGNATURE_FOLDER_ALLMINMODS = "/home/yc/thesis/NCI-16/0-Signatures/allminmods/sig_50_2"
RESULT_FOLDER_ALLMINMODS = "/home/yc/thesis/NCI-16/1-Result/2-BlackBox/sig_50_2"

# Common constants
TIMEOUT_SECONDS = 600

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_java(signature_file, ontology_file):
    """Run the Java program with the specified signature and ontology files."""
    command = [
        JAVA_EXECUTABLE, 
        "-Xmx24g", 
        "-jar",
        JAVA_JAR_PATH,
        "--ontology",
        ontology_file,
        "--sig",
        signature_file
    ]

    start_time = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    try:
        output, _ = process.communicate(timeout=TIMEOUT_SECONDS)
        elapsed_time = time.time() - start_time
        return output, elapsed_time, process.returncode
    except subprocess.TimeoutExpired:
        os.kill(process.pid, signal.SIGTERM)
        logger.warning(f"Terminated process for signature: {signature_file}")
        return None, None, None

def save_output_amm(output, folder, filename):
    os.makedirs(folder, exist_ok=True)
    sum_of_amm = 0
    average_module_size = None
    union_module_size = set()
    num_minimal_modules = None

    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        file.write(output)

    lines = output.split('\n')
    for line in lines:
        if "The size of a minimal module:" in line:
            sum_of_amm += int(line.split(":")[1].strip())
        elif line.startswith("SubClassOf") or line.startswith("EquivalentClasses"):
            union_module_size.add(line.strip())
        elif "Number of minimal modules:" in line:
            num_minimal_modules = int(line.split(":")[1].strip())

    if num_minimal_modules and num_minimal_modules > 0:
        average_module_size = sum_of_amm / num_minimal_modules

    return average_module_size, len(union_module_size), num_minimal_modules

def write_results_summary_to_csv(results_amm, csv_path):
    """Write AMM results to CSV."""
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Signature', 'AMM_Time', 'Average_MM_Size', 'Union_AMM_Size', 'Number_MM']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result_amm in results_amm:
            writer.writerow({
                'Signature': result_amm['Signature'],
                'AMM_Time': result_amm['Time Spent AMM'],
                'Average_MM_Size': result_amm['Average MM Size'],
                'Union_AMM_Size': result_amm['Union of AMM Size'],
                'Number_MM': result_amm['Number of Minimal Modules']
            })

def main():
    results_amm = []
    filenames_amm = os.listdir(SIGNATURE_FOLDER_ALLMINMODS)
    filenames_amm.sort(key=lambda f: int(os.path.splitext(f)[0]))

    for filename in filenames_amm:
        logger.info(f"Running AllMinMods for signature: {filename}")
        sig_file_amm = os.path.join(SIGNATURE_FOLDER_ALLMINMODS, filename)
        
        output_amm, time_spent_amm, returncode = run_java(sig_file_amm, ONTOLOGY_PATH)

        if returncode == 0:
            average_mm_size, union_amm_size, number_of_mm = save_output_amm(output_amm, RESULT_FOLDER_ALLMINMODS, f"{os.path.splitext(filename)[0]}.txt")
            result_data = {
                'Signature': filename,
                'Time Spent AMM': time_spent_amm,
                'Average MM Size': average_mm_size,
                'Union of AMM Size': union_amm_size,
                'Number of Minimal Modules': number_of_mm
            }
        else:
            logger.warning(f"Skipping AllMinMods for signature {filename} due to error or timeout")
            result_data = {
                'Signature': filename,
                'Time Spent AMM': 'NA',
                'Average MM Size': 'NA',
                'Union of AMM Size': 'NA',
                'Number of Minimal Modules': 'NA'
            }
        results_amm.append(result_data)

            

    # Write AMM results to CSV
    results_summary_csv_path = os.path.join(RESULT_FOLDER_ALLMINMODS, 'results_summary.csv')
    write_results_summary_to_csv(results_amm, results_summary_csv_path)

if __name__ == "__main__":
    main()
