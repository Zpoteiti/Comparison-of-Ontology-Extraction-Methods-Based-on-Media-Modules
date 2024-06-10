import subprocess
import os
import csv
import time
import signal
import logging

# Constants
MEX_EXECUTABLE = "./mex.bin"
ONTOLOGY_PATH = "/home/yc/thesis/snomedCT/external_data&program/snomedct012016.krss.owl"
SIGNATURE_FOLDER = "/home/yc/thesis/snomedCT/0_sig/mex"
RESULT_FOLDER = "/home/yc/thesis/snomedCT/1_result/1-sentimen_module"
TIMEOUT = 600

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        output, _ = process.communicate(timeout=TIMEOUT)
        elapsed_time = time.time() - start_time
        return output, elapsed_time, process.returncode
    except subprocess.TimeoutExpired:
        os.kill(process.pid, signal.SIGTERM)
        logger.warning(f"Terminated process for signature: {signature_file}")
        return None, None, None
    except Exception as e:
        logger.error(f"Error running MEX for signature {signature_file}: {e}")
        return None, None, None

# Function to save relevant output to a text file
def save_output(output, folder, id):
    filename = f"{id}.krss"
    directory = os.path.join(RESULT_FOLDER, folder)
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as file:
        file.write(output)

# Function to write results to CSV file
def write_to_csv(results, folder, result_folder):
    csv_name = folder + '_mex_results.csv'
    file_path = os.path.join(result_folder, csv_name)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Signature', 'Time Spent'])
        for result in results:
            writer.writerow(result)

# Main function
def main(signature_folder, result_folder):
    folder = os.path.basename(signature_folder.rstrip('/'))  # Extract folder name from signature folder path
    results = []

    filenames = os.listdir(signature_folder)
    filenames.sort(key=lambda f: int(f))  # Sort filenames numerically

    for filename in filenames:
        signature_file = os.path.join(signature_folder, filename)
        id = os.path.basename(signature_file)
        logger.info(f"Running MEX for Signature: {id}")

        output, elapsed_time, returncode = run_mex(signature_file)
        if returncode == 0:
            save_output(output, folder, id)  # Save output with folder and id
            results.append([filename, elapsed_time])
        else:
            logger.warning(f"Skipping signature {id} due to error or timeout")
            results.append([filename, 'NA'])

    write_to_csv(results, folder, result_folder)  # Write results to CSV
    logger.info("Results written to mex_results.csv")

if __name__ == "__main__":
    main(SIGNATURE_FOLDER, RESULT_FOLDER)
