import os

def convert_to_krss(axioms):
    return axioms.replace('SubClassOf(', '(implies ') \
                 .replace('EquivalentClasses(', '(equivalent ') \
                 .replace('ObjectSomeValuesFrom(', '(some ') \
                 .replace('ObjectIntersectionOf(', '(and ') \
                 .replace('SubObjectPropertyOf(', '(implies-role ')

def convert_file_to_krss(input_file):
    output_file = os.path.splitext(input_file)[0] + '.krss.owl'
    with open(input_file, 'r') as f:
        data = f.readlines()
    
    with open(output_file, 'w') as f:
        for line in data:
            if line.startswith(('Prefix', 'Declaration')):
                continue
            elif line.startswith(('Class(', 'ObjectProperty(')):
                line_krss = convert_to_krss(line)
                line_new = line_krss.replace("<", "").replace(">", "")
                f.write(line_new)
            else:
                f.write(line)

    print(f'Conversion completed. Output file saved as: {output_file}')

# Provide the path to your OWL file here
input_owl_file = r'C:\Users\zpote\OneDrive\Document\thesis\formod-main\workspace\covid19_bogMod\sig_covid19_bigMod.owl_annotated.owl'
convert_file_to_krss(input_owl_file)
