import os

def extract_urls(text):
    urls = []
    start = text.find("[") + 1
    end = text.find("]")
    urls_text = text[start:end]
    urls = urls_text.split("\n")
    urls = [url.strip() for url in urls if url.strip()]
    return urls

def format_urls(urls):
    return ' '.join(urls)

if __name__ == "__main__":
    # Specify the path where the signature files are located
    signature_folder = r"/home/yc/thesis/snomedCT/0_sig/zoom"

    # Specify the path for the output folder
    output_folder = r"/home/yc/thesis/snomedCT/0_sig/formod"

    # Loop through each signature file in the specified directory
    for file_name in os.listdir(signature_folder):
        input_file = os.path.join(signature_folder, file_name)
        output_file = os.path.join(output_folder, f"{file_name}")

        # Reading input from the signature file
        with open(input_file, "r") as file:
            input_text = file.read()

        classes_text, roles_text = input_text.split("Roles[")

        classes_urls = extract_urls(classes_text)
        formatted_classes = format_urls(classes_urls)

        roles_urls = extract_urls(roles_text)
        formatted_roles = format_urls(roles_urls)

        # Writing output to a new file in the output folder
        with open(output_file, "w") as file:
            file.write(formatted_classes + "\n")
            file.write(formatted_roles)
