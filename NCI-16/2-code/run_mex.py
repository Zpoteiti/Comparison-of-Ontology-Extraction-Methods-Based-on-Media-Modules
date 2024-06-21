import subprocess
import os
import csv
import time
import signal
import logging

# Constants
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/NCI-16/external_program&data/ISWC17.jar"
MEX_EXECUTABLE = "/home/yc/thesis/NCI-16/external_program&data/mex.bin"
ALL_MIN_MODS_JAR = "/home/yc/thesis/NCI-16/external_program&data/AllMinMods.jar"
ONTOLOGY_PATH = "/home/yc/thesis/NCI-16/external_program&data/nci-16.krss.owl"      # Path to the KRSS ontology file
SIGNATURE_FOLDER_MEX = "/home/yc/thesis/NCI-16/0-Signatures_nci16/MEX/sig_50_1"
RESULT_FOLDER_MEX = "/home/yc/thesis/NCI-16/1-result/1-sentiment_module/sig_50_1"
RESULT_FOLDER_ALL_MIN_MODS = "/home/yc/thesis/NCI-16/1-result/2-final_mex/sig_50_1"
TIMEOUT_SECONDS = 600  # Timeout for both MEX and AllMinMods (in seconds)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_signatures_for_MEX(input_directory, output_directory):
    """Translate signatures for AllMinMods."""
    # Create the output directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)

    # Iterate through files in the input directory
    for filename in os.listdir(input_directory):
        # Ensure we process files starting with digits
        if filename.isdigit():
            # Construct the full file paths
            input_filepath = os.path.join(input_directory, filename)
            output_filepath = os.path.join(output_directory, filename)

            # Read the content of the input file
            with open(input_filepath, 'r') as infile:
                content = infile.read()

            # Perform the required translations
            content = content.replace("Classes", "concepts ")
            content = content.replace("Roles[", "roles [")

            # Write the modified content to the output file
            with open(output_filepath, 'w') as outfile:
                outfile.write(content)

            logger.info(f"Translated signature file for AllMinMods: {filename}")

    logger.info("Translation for AllMinMods completed successfully.")

def run_mex(signature_file):
    """Run MEX with a given signature file."""
    command = [
        MEX_EXECUTABLE,
        "-tbx",
        ONTOLOGY_PATH_MEX,
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
        logger.warning(f"Terminated MEX process for signature: {signature_file}")
        return None, None, None

def run_all_min_mods(signature_file):
    """Run AllMinMods with a given signature file."""
    command = [
        JAVA_EXECUTABLE,
        "-Xmx24g",
        "-jar",
        ALL_MIN_MODS_JAR,
        "--ontology",
        ONTOLOGY_PATH_MEX,
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
        logger.warning(f"Terminated AllMinMods process for signature: {signature_file}")
        return None, None, None

def extract_information_from_mex_result(file_path):
    """Extract information from the result of MEX."""
    signature = os.path.splitext(os.path.basename(file_path))[0]
    line_count = count_lines_in_file(file_path)
    return {
        'Signature': signature,
        'Sentiment M size': line_count
    }

def extract_information_from_all_min_mods_result(file_path):
    """Extract information from the result of AllMinMods."""
    signature = os.path.splitext(os.path.basename(file_path))[0]
    data = extract_information(file_path)  # Assuming this function exists and extracts the required information
    return {
        'Signature': signature,
        'First Minimal Module Size': data['First Minimal Module Size'],
        'Union of All Module Size': data['Union of All Module Size'],
        'Number of Minimal Modules': data['Number of Minimal Modules']
    }

def count_lines_in_file(file_path):
    """Count the number of lines in a file."""
    with open(file_path, 'r') as file:
        return sum(1 for line in file)

def get_expected_files(directory, total_files):
    """Generate the list of expected files based on the total number of files expected."""
    expected_files = [os.path.join(directory, f"{i}.krss") for i in range(total_files)]
    return expected_files

def main():
    # Step 1: Translate signatures for MEX
    translate_signatures_for_MEX(SIGNATURE_FOLDER_MEX, SIGNATURE_FOLDER_MEX)

    # Step 2: Run MEX and save results
    expected_files_mex = get_expected_files(SIGNATURE_FOLDER_MEX, 100)
    results_mex = []
    
    for file_path in expected_files_mex:
        if os.path.exists(file_path):
            output, elapsed_time, returncode = run_mex(file_path)
            if returncode == 0:
                result_data = extract_information_from_mex_result(file_path)
                results_mex.append(result_data)
                logger.info(f"Processed MEX for signature: {file_path}")
            else:
                logger.warning(f"Skipping MEX for signature {file_path} due to error or timeout")
        else:
            logger.warning(f"File not found: {file_path}")

    # Write MEX results to CSV
    mex_result_csv_path = os.path.join(RESULT_FOLDER_MEX, 'mex_results.csv')
    write_mex_results_to_csv(results_mex, mex_result_csv_path)

    # Step 3: Run AllMinMods and save results
    expected_files_all_min_mods = get_expected_files(TRANSLATED_SIGNATURE_FOLDER_ALL_MIN_MODS, 100)
    results_all_min_mods = []

    for file_path in expected_files_all_min_mods:
        if os.path.exists(file_path):
            output, elapsed_time, returncode = run_all_min_mods(file_path)
            if returncode == 0:
                result_data = extract_information_from_all_min_mods_result(file_path)
                results_all_min_mods.append(result_data)
                logger.info(f"Processed AllMinMods for signature: {file_path}")
            else:
                logger.warning(f"Skipping AllMinMods for signature {file_path} due to error or timeout")
        else:
            logger.warning(f"File not found: {file_path}")

    # Write AllMinMods results to CSV
    all_min_mods_result_csv_path = os.path.join(RESULT_FOLDER_ALL_MIN_MODS, 'all_min_mods_results.csv')
    write_all_min_mods_results_to_csv(results_all_min_mods, all_min_mods_result_csv_path)

    # Step 4: Combine results into a single CSV
    combine_results_into_single_csv(mex_result_csv_path, all_min_mods_result_csv_path)

    logger.info("Process completed successfully.")

def write_mex_results_to_csv(results, csv_path):
    """Write MEX results to CSV."""
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Set', 'Signature', 'Time Spent MEX', 'Sentiment M size']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, result in enumerate(results):
            writer.writerow({
                'Set': 1,  # Assuming a single set for now
                'Signature': result['Signature'],
                'Time Spent MEX': 'TODO',  # Replace with actual time spent
                'Sentiment M size': result['Sentiment M size']
            })

def write_all_min_mods_results_to_csv(results, csv_path):
    """Write AllMinMods results to CSV."""
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Set', 'Signature', 'Time Spent ISWC17', 'First Minimal Module Size', 'Union of All Module Size', 'Number of Minimal Modules']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, result in enumerate(results):
            writer.writerow({
                'Set': 1,  # Assuming a single set for now
                'Signature': result['Signature'],
                'Time Spent ISWC17': 'TODO',  # Replace with actual time spent
                'First Minimal Module Size': result['First Minimal Module Size'],
                'Union of All Module Size': result['Union of All Module Size'],
                'Number of Minimal Modules': result['Number of Minimal Modules']
            })

def combine_results_into_single_csv(mex_csv_path, all_min_mods_csv_path):
    """Combine MEX and AllMinMods results into a single CSV."""
    # Load MEX results
    mex_results = []
    with open(mex_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mex_results.append(row)

    # Load AllMinMods results
    all_min_mods_results = []
    with open(all_min_mods_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_min_mods_results.append(row)

    # Merge results based on signature
    merged_results = []
    for mex_result in mex_results:
        for all_min_mods_result in all_min_mods_results:
            if mex_result['Signature'] == all_min_mods_result['Signature']:
                merged_result = {
                    'Set': 1,  # Assuming a single set for now
                    'Signature': mex_result['Signature'],
                    'Time Spent MEX': mex_result['Time Spent MEX'],
                    'Time Spent ISWC17': all_min_mods_result['Time Spent ISWC17'],
                    'Total Time': float(mex_result['Time Spent MEX']) + float(all_min_mods_result['Time Spent ISWC17']),
                    'Sentiment M size': mex_result['Sentiment M size'],
                    'First Minimal Module Size': all_min_mods_result['First Minimal Module Size'],
                    'Union of All Module Size': all_min_mods_result['Union of All Module Size'],
                    'Number of Minimal Modules': all_min_mods_result['Number of Minimal Modules']
                }
                merged_results.append(merged_result)
                break

    # Write merged results to CSV
    final_csv_path = os.path.join(RESULT_FOLDER_ALL_MIN_MODS, 'sig_50_1_final_mex.csv')
    with open(final_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Set', 'Signature', 'Time Spent MEX', 'Time Spent ISWC17', 'Total Time', 'Sentiment M size', 'First Minimal Module Size', 'Union of All Module Size', 'Number of Minimal Modules']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in merged_results:
            writer.writerow(result)

if __name__ == "__main__":
    main()
