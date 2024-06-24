import re

file = """Prefix(owl:=<http://www.w3.org/2002/07/owl#>)

Ontology(
EquivalentClasses(<0105012> ObjectSomeValuesFrom(<127489000> <48895003>))
EquivalentClasses(<0120342> ObjectSomeValuesFrom(<127489000> <410942007>))
EquivalentClasses(<0124940> ObjectSomeValuesFrom(<272741003> <182353008>))
EquivalentClasses(<05575> ObjectSomeValuesFrom(<127489000> <373457005>))
EquivalentClasses(<07902> ObjectSomeValuesFrom(<272741003> <7771000>))
EquivalentClasses(<243964006> ObjectIntersectionOf(<07902> <8412003>))
SubClassOf(<353800005> ObjectIntersectionOf(<0105012> <17600005>))
SubClassOf(<353801009> <353800005>)
SubClassOf(<353802002> <353801009>)
SubClassOf(<372892004> <373233008>)
SubClassOf(<373233008> <410942007>)
SubClassOf(<373457005> ObjectIntersectionOf(<372892004> <406463001>))
SubClassOf(<7771000> ObjectIntersectionOf(<106233006> <182353008>))
)
    """
#split the file into lines
file = file.split("\n")
axioms = set()

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
            normalized_axiom = f"{subclass.strip()}{element.strip()}"+")"
            # Remove all white spaces after processing
            normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
            axioms.add(normalized_axiom)
    elif normalized_line.startswith("SubClassOf"):
        # Handle non-intersection SubClassOf axioms
        # Remove all white spaces after processing
        normalized_line = re.sub(r'\s+', '', normalized_line)
        axioms.add(normalized_line)

print(axioms)
