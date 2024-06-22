import csv
from pathlib import Path

def count_lines_in_file(file_path):
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r') as file:
            return sum(1 for line in file)
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return 'NA'

def get_expected_files(directory, total_files):
    """Generate the list of expected .krss files based on the total number of files expected."""
    return [directory / f"{i}.krss" for i in range(total_files)]

def main():
    # Define the directory containing the .krss files
    directory = Path('/home/yc/thesis/snomedCT/1_result/1-sentimen_module')
    
    # Define the total number of expected files
    total_files = 1000
    
    # Get the list of expected .krss files
    expected_files = get_expected_files(directory, total_files)
    
    # Create a list to store the results
    results = []

    # Iterate through the expected .krss files and count lines
    for file_path in expected_files:
        if file_path.exists():
            line_count = count_lines_in_file(file_path)
        else:
            line_count = 'NA'
        filename = file_path.name
        results.append((int(filename.split('.')[0]), filename, line_count))

    # Sort the results by the numeric part of the filename
    results.sort()

    # Write the results to a CSV file in the specified directory
    result_file = directory / 'result.csv'
    try:
        with result_file.open('w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Filename', 'Line Count'])
            for _, filename, line_count in results:
                csvwriter.writerow([filename, line_count])
        print(f"Results have been written to {result_file}")
    except IOError as e:
        print(f"Error writing to file {result_file}: {e}")

if __name__ == "__main__":
    main()
