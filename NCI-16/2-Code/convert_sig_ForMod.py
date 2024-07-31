import os

def extract_urls(text):
    start = text.find("[") + 1
    end = text.find("]")
    urls_text = text[start:end]
    urls = urls_text.split("\n")
    return [url.strip() for url in urls if url.strip()]

def format_urls(urls):
    return ' '.join(urls)

def process_signature_file(input_file, output_file):
    with open(input_file, "r") as file:
        input_text = file.read()

    classes_text, roles_text = input_text.split("Roles[")

    classes_urls = extract_urls(classes_text)
    formatted_classes = format_urls(classes_urls)

    roles_urls = extract_urls(roles_text)
    formatted_roles = format_urls(roles_urls)

    with open(output_file, "w") as file:
        file.write(formatted_classes + "\n")
        file.write(formatted_roles)

def main(signature_folder,output_folder):


    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(signature_folder):
        input_file = os.path.join(signature_folder, file_name)
        output_file = os.path.join(output_folder, file_name)

        process_signature_file(input_file, output_file)

    print(f"Processing completed. Formatted files are saved in {output_folder}")

if __name__ == "__main__":
    signature_folder = r"/home/yc/thesis/NCI-16/0-Signatures/allminmods/sig_50_1"
    output_folder = r"/home/yc/thesis/NCI-16/0-Signatures/formod/sig_50_1"
    main(signature_folder, output_folder)
