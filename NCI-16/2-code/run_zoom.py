import subprocess
import os
import csv
import time
import signal
import logging

# Constants
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/NCI-16/external_program&data/ISWC17.jar"
ONTOLOGY_PATH = "/home/yc/thesis/NCI-16/external_program&data/nci-16.owl"
SIGNATURE_FOLDER = "/home/yc/thesis/NCI-16/0-Signatures_nci16/zoom/sig_50_2"
RESULT_FOLDER = "/home/yc/thesis/NCI-16/1-result/2-final_zoom"

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to run Java program with a given signature file
def run_java(signature_file):
    command = [
        JAVA_EXECUTABLE, 
        "-Xmx24g", 
        "-jar",
        JAVA_JAR_PATH,
        "--ontology",
        ONTOLOGY_PATH,
        "--sig",
        signature_file
    ]

    start_time = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    try:
        output, _ = process.communicate(timeout=600)
        elapsed_time = time.time() - start_time
        return output, elapsed_time, process.returncode
    except subprocess.TimeoutExpired:
        os.kill(process.pid, signal.SIGTERM)
        logger.warning(f"Terminated process for signature: {signature_file}")
        return None, None, None

# Function to save relevant output to a text file
def save_output(output, result_subfolder, id):
    filename = f"{id}.txt"
    directory = os.path.join(RESULT_FOLDER, result_subfolder)
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as file:
        file.write(output)

# Function to write results to CSV file
def write_to_csv(results, result_folder, folder_name):
    csv_name = folder_name + '_java_results.csv'
    file_path = os.path.join(result_folder, csv_name)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Signature', 'Time Spent'])
        for result in results:
            writer.writerow(result)

# Main function
def main(signature_folder, result_folder):
    folder_name = os.path.basename(os.path.normpath(signature_folder))  # Extract folder name from signature folder path
    result_subfolder = os.path.join(result_folder, folder_name)  # Subfolder for individual results
    results = []

    filenames = os.listdir(signature_folder)
    filenames.sort(key=lambda f: int(f.split('.')[0]))  # Sort filenames numerically

    for filename in filenames:
        signature_file = os.path.join(signature_folder, filename)
        id = signature_file.split('/')[-1].split('.')[0]  # Get the id from the filename

        logger.info(f"Processing signature: {id}")

        output, elapsed_time, returncode = run_java(signature_file)
        if returncode == 0:
            save_output(output, result_subfolder, id)  # Pass folder variable to save_output function
            results.append([filename, elapsed_time])
        else:
            logger.warning(f"Skipping signature {id} due to error or timeout")
            results.append([filename, 'NA'])

    write_to_csv(results, result_folder, folder_name)
    logger.info(f"Results written to {folder_name}_java_results.csv")

if __name__ == "__main__":
    main(SIGNATURE_FOLDER, RESULT_FOLDER)
