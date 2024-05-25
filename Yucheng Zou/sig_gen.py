import os
import random
import re

def parse_custom_format(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    concepts = set()
    roles = set()
    for line in lines:
        if line.startswith("Declaration(Class"):
            concept = re.findall(r'<(.*?)>', line)[0]
            concepts.add(concept)
        elif line.startswith("Declaration(ObjectProperty"):
            role = re.findall(r'<(.*?)>', line)[0]
            roles.add(role)
    
    return concepts, roles

def generate_signature(file_path, num_signatures, num_concepts, num_roles, output_dir="signatures"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_signatures):
        concepts, roles = parse_custom_format(file_path)
        selected_concepts = random.sample(list(concepts), num_concepts)
        selected_roles = random.sample(list(roles), num_roles)

        signature_file = os.path.join(output_dir, str(i))
        with open(signature_file, "w") as f:
            f.write("Classes[\n" + '\n'.join(selected_concepts) + "\n]\n")
            f.write("Roles[\n" + '\n'.join(selected_roles) + "\n]\n")

file_path = r"C:\thesis\formod-main\workspace\snomedct012016\terminologyWithDeclaration.owl"
output_dir = r"C:\thesis\Signatures_snomedct16\sig_50_10"
num_signatures = 100
num_concepts = 50
num_roles = 10
generate_signature(file_path, num_signatures, num_concepts, num_roles, output_dir)
