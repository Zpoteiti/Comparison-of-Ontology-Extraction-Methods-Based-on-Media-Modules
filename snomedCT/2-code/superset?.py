import os
import csv
import re

# Directories containing the modules
SEMANTIC_MODULE_DIR = "/home/yc/thesis-main/snomedCT/1_result/1-semantic_module_xKRSS"
COMPLETE_MODULE_DIR = "/home/yc/thesis-main/snomedCT/1_result/1-complete_module"
FINAL_AMM_DIR = "/home/yc/thesis-main/snomedCT/1_result/2-final_amm"
OUTPUT_CSV_PATH = "/home/yc/thesis-main/snomedCT/1_result/semantic_complete_comparison.csv"

def load_and_filter_axioms(filepath):
    """Load and filter axioms from a file to include only EquivalentClasses or SubClassOf lines."""
    if not os.path.exists(filepath):
        return None
    
    axioms = set()
    
    with open(filepath, 'r') as file:
        for line in file:
            # Remove angle brackets
            normalized_line = re.sub(r'<(\d+)>', r'\1', line.strip())
            if normalized_line.startswith("EquivalentClasses"):
                # Remove all white spaces after processing
                normalized_line = re.sub(r'\s+', '', normalized_line)
                axioms.add(normalized_line)
            elif "ObjectIntersectionOf" in normalized_line and normalized_line.startswith("SubClassOf"):
                subclass, rest = normalized_line.split(" ObjectIntersectionOf(")
                elements = rest.strip(")").split()  # Split by white space
                for element in elements:
                    normalized_axiom = f"{subclass.strip()}{element.strip()})"
                    # Remove all white spaces after processing
                    normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
                    axioms.add(normalized_axiom)
            elif normalized_line.startswith("SubClassOf"):
                # Handle non-intersection SubClassOf axioms
                # Remove all white spaces after processing
                normalized_line = re.sub(r'\s+', '', normalized_line)
                axioms.add(normalized_line)
    
    return axioms

def compare_modules(semantic_axioms, complete_axioms, final_zoom_axioms):
    """Compare modules to check if they are supersets of final zoom axioms."""
    if final_zoom_axioms is None:
        return 'NA', 'NA'  # If final zoom axioms are missing, we cannot perform the comparison

    semantic_superset = 'NA' if semantic_axioms is None else semantic_axioms.issuperset(final_zoom_axioms)
    complete_superset = 'NA' if complete_axioms is None else complete_axioms.issuperset(final_zoom_axioms)
    return semantic_superset, complete_superset

def main():
    results = []

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

    for i in range(1000):  # Loop through 0 to 999 signatures
        semantic_filepath = os.path.join(SEMANTIC_MODULE_DIR, f"{i}.txt")
        complete_filepath = os.path.join(COMPLETE_MODULE_DIR, str(i), "approximate_module.owl")
        final_zoom_filepath = os.path.join(FINAL_AMM_DIR, f"{i}.txt")

        semantic_axioms = load_and_filter_axioms(semantic_filepath)
        complete_axioms = load_and_filter_axioms(complete_filepath)
        final_zoom_axioms = load_and_filter_axioms(final_zoom_filepath)

        semantic_superset, complete_superset = compare_modules(semantic_axioms, complete_axioms, final_zoom_axioms)

        results.append([i, semantic_superset, complete_superset])

    # Write results to CSV
    with open(OUTPUT_CSV_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Signature', 'Semantic Superset', 'Complete Superset'])
        writer.writerows(results)

    print(f"Results have been written to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main()
