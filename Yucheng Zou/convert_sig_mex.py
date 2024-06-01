import os

# Define input and output directories
input_directory = "/home/yz/thesis/Signatures_nci16/sig_50_10"
output_directory = "/home/yz/thesis/sig_MEX/sig_50_10"

# Create the output directory if it does not exist
os.makedirs(output_directory, exist_ok=True)

# Iterate through files in the input directory
for filename in os.listdir(input_directory):
    # Ensure we process files starting with "0" and having no extension
    if filename.isdigit():
        # Construct the full file path
        input_filepath = os.path.join(input_directory, filename)
        output_filepath = os.path.join(output_directory, filename)
        
        # Read the content of the input file
        with open(input_filepath, 'r') as infile:
            content = infile.read()
        
        # Replace the required strings
        content = content.replace("Classes", "concepts ")
        content = content.replace("Roles[", "roles [")
        
        # Write the modified content to the output file
        with open(output_filepath, 'w') as outfile:
            outfile.write(content)

print("Translation completed successfully.")
