import os
import csv
import re

# Directories containing the modules
SEMANTIC_MODULE_DIR = "/home/yc/thesis/NCI-16/1-Result/1-semantic_module_xKRSS/sig_50_10"
COMPLETE_MODULE_DIR = "/home/yc/thesis/NCI-16/1-Result/1-approximate_module/query_sig_10"
FINAL_AMM_DIR       = "/home/yc/thesis/NCI-16/1-Result/2-AllMinMods/sig_50_10"
OUTPUT_CSV_PATH     = "/home/yc/thesis/NCI-16/1-Result/superset?_10.csv"
SIG_NUM = 100

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
                if "ObjectIntersectionOf" in normalized_line:
                    parts = normalized_line.split("ObjectIntersectionOf(")
                    left = parts[0].strip()
                    right = parts[1].replace(")","").split()
                    right.sort()
                    normalized_axiom = f"{left}ObjectIntersectionOf({' '.join(right)}))"
                    normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
                    axioms.add(normalized_axiom)
                elif "ObjectSomeValuesFrom" in normalized_line:
                    parts = normalized_line.split("ObjectSomeValuesFrom(")
                    left = parts[0].strip()
                    right = parts[1].replace(")","").split()
                    right.sort()
                    normalized_axiom = f"{left}ObjectSomeValuesFrom({' '.join(right)}))"
                    normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
                    axioms.add(normalized_axiom)
                else:
                        elements = normalized_line.strip("EquivalentClasses(").strip("").split()
                        elements.sort()
                        normalized_axiom = f"EquivalentClasses({' '.join(elements)})"
                        normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
                        axioms.add(normalized_axiom)

            elif normalized_line.startswith("SubClassOf"):
                if "ObjectIntersectionOf" in normalized_line:
                    subclass, rest = normalized_line.split(" ObjectIntersectionOf(")
                    elements = rest.strip(")").split()  # Split by white space
                    for element in elements:
                        normalized_axiom = f"{subclass.strip()}{element.strip()})"
                        # Remove all white spaces after processing
                        normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
                        axioms.add(normalized_axiom)
                elif "ObjectSomeValuesFrom" in normalized_line:
                    parts = normalized_line.split("ObjectSomeValuesFrom(")
                    left = parts[0].strip()
                    right = parts[1].strip(")").split()
                    right.sort()
                    normalized_axiom = f"{left}ObjectSomeValuesFrom({' '.join(right)})"
                    normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
                    axioms.add(normalized_axiom)
                else:
                    # Handle non-intersection SubClassOf axioms
                    # Remove all white spaces after processing
                    normalized_axiom = re.sub(r'\s+', '', normalized_line)
                    axioms.add(normalized_axiom)
            
        return axioms

def compare_modules(semantic_axioms, complete_axioms, final_amm_axioms):
    """Compare modules to check if they are supersets of final amm axioms."""
    if final_amm_axioms is None:
        return 'NA', 'NA'  # If final amm axioms are missing, we cannot perform the comparison

    semantic_superset = 'NA' if semantic_axioms is None else semantic_axioms.issuperset(final_amm_axioms)
    complete_superset = 'NA' if complete_axioms is None else complete_axioms.issuperset(final_amm_axioms)
    return semantic_superset, complete_superset

def main():
    results = []

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

    for i in range(SIG_NUM):
        semantic_filepath = os.path.join(SEMANTIC_MODULE_DIR, f"{i}.txt")
        complete_filepath = os.path.join(COMPLETE_MODULE_DIR, str(i), "approximate_module.owl")
        final_amm_filepath = os.path.join(FINAL_AMM_DIR, f"{i}-1.txt")

        semantic_axioms = load_and_filter_axioms(semantic_filepath)
        complete_axioms = load_and_filter_axioms(complete_filepath)
        final_amm_axioms = load_and_filter_axioms(final_amm_filepath)

        semantic_superset, complete_superset = compare_modules(semantic_axioms, complete_axioms, final_amm_axioms)

        results.append([i, semantic_superset, complete_superset])

    # Write results to CSV
    with open(OUTPUT_CSV_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Signature', 'Semantic Superset', 'Complete Superset'])
        writer.writerows(results)

    print(f"Results have been written to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main()