import os
import csv
import subprocess
import time
import signal
import logging

# Constants for MEX
MEX_EXECUTABLE = "./mex.bin"
ONTOLOGY_PATH = "/home/yc/thesis/NCI-16/external_program&data/nci-16.krss.owl"
SIGNATURE_FOLDER_MEX = "/home/yc/thesis/NCI-16/0-Signatures/MEX/sig_50_2/"
RESULT_FOLDER_MEX = "/home/yc/thesis/NCI-16/1-result/1-sementic/sig_50_2/"

# Constants for AllMinMods
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/NCI-16/external_program&data/AllMinMods.jar"
SIGNATURE_FOLDER_ALLMINMODS = "/home/yc/thesis/NCI-16/0-Signatures/AllMinMods/sig_50_2/"
RESULT_FOLDER_ALLMINMODS = "/home/yc/thesis/NCI-16/1-result/2-mex/sig_50_2/"

# Common constants
TIMEOUT_SECONDS = 600

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to translate signatures for AllMinMods
def translate_signatures(input_directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.isdigit():
            input_filepath = os.path.join(input_directory, filename)
            output_filepath = os.path.join(output_directory, filename)

            with open(input_filepath, 'r') as infile:
                content = infile.read()

            content = content.replace("Classes", "concepts ")
            content = content.replace("Roles[", "roles [")

            with open(output_filepath, 'w') as outfile:
                outfile.write(content)

    logger.info("Translation of signatures completed.")

# Function to run MEX program with a given signature file
def run_mex(signature_file):
    command = [
        MEX_EXECUTABLE, 
        "-tbx",
        ONTOLOGY_PATH,
        "-sig",
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
        logger.warning(f"Timeout: {signature_file}")
        return None, None, None

def run_java(signature_file, module_file):
    """Run the Java program with the specified signature and module files."""
    command = [
        JAVA_EXECUTABLE, 
        "-Xmx24g", 
        "-jar",
        JAVA_JAR_PATH,
        "--ontology",
        module_file,
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

def save_output_mex(output, folder, filename):
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        file.write(output)

    # Calculate the size of the semantic module without reopening the file
    size_sementic = count_lines_in_file(filepath)

    return size_sementic

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

def count_lines_in_file(file_path):
    """Count the number of lines in a file."""
    with open(file_path, 'r') as file:
        return sum(1 for line in file)

def write_results_summary_to_csv(results_mex, results_amm, csv_path):
    """Write MEX and semantic size results to CSV."""
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Signature', 'Mex_Time', 'AMM_Time', 'Total_Time', 'Sementic_Size', 'Average_MM_Size', 'Union_AMM_Size', 'Number_MM']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result_mex, result_amm in zip(results_mex, results_amm):
            writer.writerow({
                'Signature': result_mex['Signature'],
                'Mex_Time': result_mex['Time MEX'],
                'AMM_Time': result_amm['Time Spent AMM'],
                'Total_Time': result_amm['Total Time'],
                'Sementic_Size': result_mex['Sementic Size'],
                'Average_MM_Size': result_amm['Average MM Size'],
                'Union_AMM_Size': result_amm['Union of AMM Size'],
                'Number_MM': result_amm['Number of Minimal Modules']
            })

def main():
    # Step 1: Translate signatures for MEX
    translate_signatures(SIGNATURE_FOLDER_ALLMINMODS, SIGNATURE_FOLDER_MEX)

    # Step 2: Run MEX with signatures and save results
    results_mex = []

    filenames_mex = os.listdir(SIGNATURE_FOLDER_MEX)
    filenames_mex.sort(key=lambda f: int(os.path.splitext(f)[0]))  # Sort numerically by filename

    for filename in filenames_mex:
        sig_file_mex = os.path.join(SIGNATURE_FOLDER_MEX, filename)
        logger.info(f"Running MEX for Signature: {filename}")

        output_mex, time_spent_mex, returncode = run_mex(sig_file_mex)

        if returncode == 0:
            size_sementic = save_output_mex(output_mex, RESULT_FOLDER_MEX, f"{os.path.splitext(filename)[0]}.krss")
            result_data = {
                'Signature': filename,
                'Time MEX': time_spent_mex,
                'Sementic Size': size_sementic
            }
        else:
            logger.warning(f"Skipping MEX for signature {filename} due to error or timeout")
            result_data = {
                'Signature': filename,
                'Time MEX': 'NA',
                'Sementic Size': 'NA'
            }
        results_mex.append(result_data)

    # Step 3: Run AllMinMods with corresponding signature and module
    results_amm = []
    filenames_amm = os.listdir(SIGNATURE_FOLDER_ALLMINMODS)
    filenames_amm.sort(key=lambda f: int(os.path.splitext(f)[0]))

    for filename in filenames_amm:
        logger.info(f"Running AllMinMods for signature: {filename}")
        sig_file_amm = os.path.join(SIGNATURE_FOLDER_ALLMINMODS, filename)
        module_file = os.path.join(RESULT_FOLDER_MEX, f"{filename}.krss")
        if not os.path.exists(module_file):
            logger.warning(f"Module file does not exist: {module_file}")
            result_data = {
                'Time Spent AMM': 'NA',
                'Total Time': 'NA',
                'Average MM Size': 'NA',
                'Union of AMM Size': 'NA',
                'Number of Minimal Modules': 'NA'
            }
            results_amm.append(result_data)
            continue
        
        output_amm, time_spent_amm, returncode = run_java(sig_file_amm, module_file)

        if returncode == 0:
            average_mm_size, union_amm_size, number_of_mm = save_output_amm(output_amm, RESULT_FOLDER_ALLMINMODS, f"{os.path.splitext(filename)[0]}.txt")
            result_data = {
                'Time Spent AMM': time_spent_amm,
                'Total Time': time_spent_amm + results_mex[int(filename)]['Time MEX'] if results_mex[int(filename)]['Time MEX'] != 'NA' else 'NA',
                'Average MM Size': average_mm_size,
                'Union of AMM Size': union_amm_size,
                'Number of Minimal Modules': number_of_mm
            }
        else:
            logger.warning(f"Skipping AllMinMods for signature {filename} due to error or timeout")
            result_data = {
                'Time Spent AMM': 'NA',
                'Total Time': 'NA',
                'Average MM Size': 'NA',
                'Union of AMM Size': 'NA',
                'Number of Minimal Modules': 'NA'
            }
        results_amm.append(result_data)

    # Write MEX results and semantic size to CSV
    results_summary_csv_path = os.path.join(RESULT_FOLDER_ALLMINMODS, 'results_summary.csv')
    write_results_summary_to_csv(results_mex, results_amm, results_summary_csv_path)

if __name__ == "__main__":
    main()
