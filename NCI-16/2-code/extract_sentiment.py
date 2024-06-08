import os
import csv

def count_lines_in_file(file_path):
    """Count the number of lines in a file."""
    with open(file_path, 'r') as file:
        return sum(1 for line in file)

def get_expected_files(directory, total_files):
    """Generate the list of expected .krss files based on the total number of files expected."""
    expected_files = [os.path.join(directory, f"{i}.krss") for i in range(total_files)]
    return expected_files

def main():
    # Define the directory containing the .krss files
    directory = '/home/yc/thesis/nci16 related/result_mex/sig_50_10'
    
    # Define the total number of expected files
    total_files = 100
    
    # Get the list of expected .krss files
    expected_files = get_expected_files(directory, total_files)
    
    # Create a list to store the results
    results = []

    # Iterate through the expected .krss files and count lines
    for file_path in expected_files:
        if os.path.exists(file_path):
            line_count = count_lines_in_file(file_path)
        else:
            line_count = 'NA'
        filename = os.path.basename(file_path)
        results.append((int(filename.split('.')[0]), filename, line_count))

    # Sort the results by the numeric part of the filename
    results.sort()

    # Write the results to a CSV file
    with open('result.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Filename', 'Line Count'])
        for _, filename, line_count in results:
            csvwriter.writerow([filename, line_count])

    print("Results have been written to result.csv")

if __name__ == "__main__":
    main()
