import subprocess
import os
import csv
import time
import signal
import logging

# Constants
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/NCI-16/external_program&data/ISWC17.jar"
SIGNATURE_FOLDER = "/home/yc/thesis/NCI-16/0-Signatures_nci16/sig_MEX/sig_50_10"
RESULT_FOLDER = "/home/yc/thesis/NCI-16/1-result/2-final_mex"
MODULES_FOLDER = "/home/yc/thesis/NCI-16/1-result/1-sentiment_module/sig_50_10"
TIMEOUT_SECONDS = 600  # Timeout for the Java process (in seconds)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def save_output(output, result_subfolder, id):
    """Save the output of the Java program to a text file."""
    filename = f"{id}.txt"
    directory = os.path.join(result_subfolder)
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as file:
        file.write(output)

def write_to_csv(results, result_csv_folder, folder_name):
    """Write the collected results to a CSV file."""
    csv_name = folder_name + '_mex+zoom_results.csv'
    file_path = os.path.join(result_csv_folder, csv_name)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Signature', 'Time Spent'])
        for result in results:
            writer.writerow(result)

def process_signature(signature_file, module_file, result_subfolder, index):
    """Process an individual signature file with its corresponding module."""
    logger.info(f"Running signature: {signature_file} with module: {module_file}")
    output, elapsed_time, returncode = run_java(signature_file, module_file)
    if returncode == 0:
        save_output(output, result_subfolder, index)
        return [os.path.basename(signature_file), elapsed_time]
    else:
        logger.warning(f"Skipping signature {signature_file} due to error or timeout")
        return [os.path.basename(signature_file), 'NA']

def main(signature_folder, result_folder, modules_folder):
    folder_name = os.path.basename(os.path.normpath(signature_folder))  # Extract folder name from signature folder path
    result_subfolder = os.path.join(result_folder, folder_name)  # Subfolder for individual results
    results = []

    filenames = sorted(os.listdir(signature_folder), key=lambda f: int(f.split('.')[0]))  # Sort filenames numerically

    for i, filename in enumerate(filenames):
        signature_file = os.path.join(signature_folder, filename)
        module_file = os.path.join(modules_folder, f"{i}.krss")
        if not os.path.exists(module_file):
            logger.warning(f"Module file does not exist: {module_file}")
            results.append([filename, 'NA'])
            continue

        result = process_signature(signature_file, module_file, result_subfolder, i)
        results.append(result)

    write_to_csv(results, result_folder, folder_name)
    logger.info(f"Results written to {folder_name}_mex+zoom_results.csv")

if __name__ == "__main__":
    main(SIGNATURE_FOLDER, RESULT_FOLDER, MODULES_FOLDER)
