import requests
import re
import json

def main():
    url = "https://etesty.md.gov.cz/ro/DLArea/Index?id=99"

    try:
        # Download the content from the URL
        print(f"Downloading {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        # Load into memory
        html_content = response.text
        
        # Grep/Extract the questionList variable
        # The pattern looks for 'const questionList=' followed by an array [...]
        # re.DOTALL allows the dot to match newlines, handling multi-line arrays
        pattern = r"const questionList\s*=\s*(\[.*?\])"
        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            question_list_str = match.group(1)
            
            # Parse the string into a Python list
            question_list = json.loads(question_list_str)
            
            print("Successfully extracted questionList")
            # print(question_list)
            print(f"Total questions found: {len(question_list)}")
        else:
            print("Could not find 'questionList' in the downloaded content.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading URL: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing question list: {e}")

if __name__ == "__main__":
    main()
