import requests
import re
import json
import os

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

            # Create the main media directory
            media_dir = "media"
            os.makedirs(media_dir, exist_ok=True)
            print(f"Created '{media_dir}' directory.")

            # Create a subfolder for each question and download details
            for question in question_list:
                # Extract the ID from the question object
                # Assuming the key is 'id'. If the structure differs, this might need adjustment.
                q_id = question.get('id')
                
                if q_id is None:
                    print(f"Skipping question with missing ID: {question}")
                    continue

                question_folder_name = f"question_{q_id}"
                question_path = os.path.join(media_dir, question_folder_name)
                os.makedirs(question_path, exist_ok=True)
                
                # Download the JSON for this specific question
                api_url = f"https://etesty.md.gov.cz/api/v1/PublicWeb/Question/{q_id}"
                try:
                    print(f"Downloading details for ID {q_id}...")
                    q_response = requests.get(api_url)
                    q_response.raise_for_status()
                    
                    # Save the JSON content to a file in the subfolder
                    output_file_path = os.path.join(question_path, "question.json")
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(q_response.text)
                        
                except Exception as e:
                    print(f"Error downloading/saving question {q_id}: {e}")
            
            print("Finished processing questions.")

        else:
            print("Could not find 'questionList' in the downloaded content.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading URL: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing question list: {e}")

if __name__ == "__main__":
    main()
