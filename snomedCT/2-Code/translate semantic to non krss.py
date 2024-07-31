import os

# Define paths
SEMANTIC_MODULE_DIR = "/home/yc/thesis-main/snomedCT/1_result/1-semantic_module"
TRANSLATED_SEMANTIC_MODULE_DIR = "/home/yc/thesis-main/snomedCT/1_result/1-semantic_module_xKRSS"

# Function to translate KRSS format to non-KRSS format
def translate_krss_to_non_krss(axioms):
    translated_axioms = []

    for line in axioms:
        line = line.strip()

        if line.startswith("(define-concept"):
            concept = line.split()[1]
            expression = line.split(maxsplit=2)[2][:-1]  # remove the closing parenthesis
            expression = expression.replace("(and ", "ObjectIntersectionOf(")
            expression = expression.replace("(some ", "ObjectSomeValuesFrom(")
            translated_axioms.append(f"EquivalentClasses(<{concept}> {expression})")

        elif line.startswith("(define-primitive-concept"):
            concept = line.split()[1]
            expression = line.split(maxsplit=2)[2][:-1]  # remove the closing parenthesis
            if "(and " in expression:
                expression = expression.replace("(and ", "ObjectIntersectionOf(")
                translated_axioms.append(f"SubClassOf(<{concept}> {expression})")
            else:
                translated_axioms.append(f"SubClassOf(<{concept}> <{expression}>)")

    return translated_axioms

# Function to translate and store KRSS files
def translate_and_store_krss_files(input_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".krss"):
            input_filepath = os.path.join(input_dir, filename)
            output_filepath = os.path.join(output_dir, filename.replace(".krss", ".txt"))
            
            with open(input_filepath, 'r') as infile:
                content = infile.readlines()
                translated_content = translate_krss_to_non_krss(content)
                
            with open(output_filepath, 'w') as outfile:
                outfile.write("\n".join(translated_content))
                
            print(f"Translated and stored {filename} to {output_filepath}")

def main():
    translate_and_store_krss_files(SEMANTIC_MODULE_DIR, TRANSLATED_SEMANTIC_MODULE_DIR)
    print("All files have been translated and stored.")

if __name__ == "__main__":
    main()
