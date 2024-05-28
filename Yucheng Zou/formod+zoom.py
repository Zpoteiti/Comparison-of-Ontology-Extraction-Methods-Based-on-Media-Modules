import subprocess
import os
import csv
import time
import signal
import logging

# Constants
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/ISWC17.jar"
SIGNATURE_FOLDER = "/home/yc/thesis/Signatures_nci16/sig_50_3"
RESULT_FOLDER = "/home/yc/thesis/result_nci-16_formod+zoom"
MODULES_FOLDER = "/home/yc/thesis/Approximate module/query_sig_3"
TIMEOUT_SECONDS = 600  # Timeout for the Java process (in seconds)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to run Java program with a given signature file and ontology module
def run_java(signature_file, module_file):
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

# Function to save relevant output to a text file
def save_output(output, folder, id):
    filename = f"{id}.txt"
    directory = os.path.join(RESULT_FOLDER, folder)
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as file:
        file.write(output)

# Function to write results to CSV file
def write_to_csv(results, folder, result_folder):
    csv_name = folder + '_formod+zoom.csv'
    file_path = os.path.join(result_folder, csv_name)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Signature', 'Time Spent'])
        for result in results:
            writer.writerow(result)

# Main function
def main(signature_folder, result_folder, modules_folder):
    folder = signature_folder.split('/')[-1]  # Extract folder name from signature folder path
    results = []

    filenames = sorted(os.listdir(signature_folder), key=lambda f: int(f.split('.')[0]))  # Sort filenames numerically

    for i, filename in enumerate(filenames):
        signature_file = os.path.join(signature_folder, filename)
        module_file = os.path.join(modules_folder, str(i), "approximate_module.owl")
        if not os.path.exists(module_file):
            logger.warning(f"Module file does not exist: {module_file}")
            continue

        logger.info(f"Running signature: {filename} with module: {module_file}")

        output, elapsed_time, returncode = run_java(signature_file, module_file)
        if returncode == 0:
            save_output(output, folder, i)
            results.append([filename, elapsed_time])
        else:
            logger.warning(f"Skipping signature {filename} due to error or timeout")
            results.append([filename, 'NA'])

    write_to_csv(results, folder, result_folder)
    logger.info("Results written to formod+zoom.csv")

if __name__ == "__main__":
    main(SIGNATURE_FOLDER, RESULT_FOLDER, MODULES_FOLDER)
