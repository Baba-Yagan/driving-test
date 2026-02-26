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
            print(f"Total questions found: {len(question_list)}")

            # Create the main media directory
            media_dir = "media"
            os.makedirs(media_dir, exist_ok=True)
            print(f"Created '{media_dir}' directory.")

            # Counters for progress tracking
            total_questions = len(question_list)
            downloaded_count = 0
            skipped_count = 0

            # Create a subfolder for each question and download details
            for index, question in enumerate(question_list, 1):
                question_folder_name = f"question_{question}"
                question_path = os.path.join(media_dir, question_folder_name)
                os.makedirs(question_path, exist_ok=True)
                
                output_file_path = os.path.join(question_path, "question.json")

                # Check if file already exists
                if os.path.exists(output_file_path):
                    skipped_count += 1
                else:
                    # Download the JSON for this specific question
                    api_url = f"https://etesty.md.gov.cz/api/v1/PublicWeb/Question/{question}"
                    try:
                        q_response = requests.get(api_url)
                        q_response.raise_for_status()
                        
                        # Save the JSON content to a file in the subfolder
                        with open(output_file_path, 'w', encoding='utf-8') as f:
                            f.write(q_response.text)
                        
                        downloaded_count += 1
                            
                    except Exception as e:
                        # Print error on a new line so it doesn't get overwritten by progress
                        print(f"\nError downloading/saving question {question}: {e}")

                # Update progress on the same line
                print(f"Progress: {index}/{total_questions} | Downloaded: {downloaded_count} | Skipped: {skipped_count}", end='\r')
            
            # Print a new line at the end to separate the final progress message from the next output
            print()
            print(f"Finished processing questions. Downloaded: {downloaded_count}, Skipped: {skipped_count}.")

            # --- Second Iteration: Download Media ---
            print("\nStarting media download...")
            media_downloaded = 0
            media_skipped = 0
            media_errors = 0

            for index, question in enumerate(question_list, 1):
                question_folder_name = f"question_{question}"
                question_path = os.path.join(media_dir, question_folder_name)
                json_path = os.path.join(question_path, "question.json")

                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            q_data = json.load(f)

                        # Check if mediaContent exists
                        if q_data.get("mediaContent"):
                            media_url_relative = q_data["mediaContent"].get("mediaUrl")

                            if media_url_relative:
                                # Extract the actual filename from the URL to ensure correct extension
                                actual_filename = os.path.basename(media_url_relative)
                                
                                # Update the JSON object to reflect the correct filename
                                q_data["mediaContent"]["printMediaName"] = actual_filename
                                
                                # Save the updated JSON back to the file
                                try:
                                    with open(json_path, 'w', encoding='utf-8') as f:
                                        json.dump(q_data, f, ensure_ascii=False)
                                except Exception as e:
                                    print(f"\nError updating JSON for question {question}: {e}")

                                # Construct full URL
                                base_url = "https://etesty.md.gov.cz"
                                full_media_url = f"{base_url}{media_url_relative}"
                                media_save_path = os.path.join(question_path, actual_filename)

                                if os.path.exists(media_save_path):
                                    media_skipped += 1
                                else:
                                    try:
                                        m_response = requests.get(full_media_url)
                                        m_response.raise_for_status()
                                        
                                        # Write binary content
                                        with open(media_save_path, 'wb') as mf:
                                            mf.write(m_response.content)
                                        
                                        media_downloaded += 1
                                    except Exception as e:
                                        media_errors += 1
                                        print(f"\nError downloading media for question {question}: {e}")
                    except Exception as e:
                        print(f"\nError parsing JSON for question {question}: {e}")
                
                # Update progress on the same line
                print(f"Media Progress: {index}/{total_questions} | Downloaded: {media_downloaded} | Skipped: {media_skipped} | Errors: {media_errors}", end='\r')

            print()
            print(f"Finished processing media. Downloaded: {media_downloaded}, Skipped: {media_skipped}, Errors: {media_errors}.")
            # ---------------------------------------

        else:
            print("Could not find 'questionList' in the downloaded content.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading URL: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing question list: {e}")

if __name__ == "__main__":
    main()
