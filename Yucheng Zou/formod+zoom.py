import subprocess
import os
import logging

# Constants
JAVA_EXECUTABLE = "java"
JAVA_JAR_PATH = "/home/yc/thesis/ISWC17.jar"
SIGNATURE_FOLDER = "/home/yc/thesis/Signatures_nci16/sig_50_1"
ONTOLOGY_BASE_PATH = "/home/yc/thesis/Approximate_module/query_sig_1"

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to run Java program with given ontology and signature files
def run_java(ontology_file, signature_file):
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

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, _ = process.communicate()
    return output, process.returncode

# Main function to iterate through signature files and execute Java program
def main():
    signature_files = sorted(os.listdir(SIGNATURE_FOLDER), key=lambda f: int(f))
    
    for signature in signature_files:
        ontology_file = os.path.join(ONTOLOGY_BASE_PATH, signature, "approximate_module.owl")
        signature_file = os.path.join(SIGNATURE_FOLDER, signature)

        logger.info(f"Running for Signature: {signature}")
        output, returncode = run_java(ontology_file, signature_file)
        if returncode == 0:
            logger.info(f"Completed Signature: {signature} successfully.")
        else:
            logger.warning(f"Failed to complete Signature: {signature}")

if __name__ == "__main__":
    main()
