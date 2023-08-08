import os

def search_in_files(directory, search_texts):
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read().lower()
                    if all(text.strip().lower() in content for text in search_texts):
                        print(f"Found in {file_path}")
            except:
                print(f"Could not read {file_path}")

input_text = input("Please enter the text you want to search for (use & to separate multiple keywords): ")
search_texts = input_text.split('&')
directory = os.getcwd() # Gets the current working directory

search_in_files(directory, search_texts)
