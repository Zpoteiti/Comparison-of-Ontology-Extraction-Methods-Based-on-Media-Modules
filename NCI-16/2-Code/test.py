import re
axioms = set()
line = "SubClassOf(<13377> ObjectIntersectionOf(13446  05746  ))"
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
        right = parts[1].replace(")","").split()
        right.sort()
        normalized_axiom = f"{left}ObjectSomeValuesFrom({' '.join(right)}))"
        normalized_axiom = re.sub(r'\s+', '', normalized_axiom)
        axioms.add(normalized_axiom)
    else:
        # Handle non-intersection SubClassOf axioms
        # Remove all white spaces after processing
        normalized_axiom = re.sub(r'\s+', '', normalized_line)
        axioms.add(normalized_axiom)

print(axioms)