def to_json(data):
    return json.dumps(data, indent=2)

def to_xml(data):
    root = ET.Element("prompt")
    for k,v in data.items():
        node = ET.SubElement(root, k)
        node.text = v
    return ET.tostring(root, encoding="unicode")

def to_yaml(data):
    if not yaml: return "YAML unavailable"
    return yaml.dump(data)

def to_markdown(data):
    out = []
    for k,v in data.items():
        out.append(f"### {k.capitalize()}\n{v}\n")
    return "\n".join(out)


