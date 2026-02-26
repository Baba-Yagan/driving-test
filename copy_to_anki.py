import os
import shutil
from pathlib import Path
from datetime import datetime

def main():
    # Define paths
    anki_base_path = Path.home() / ".local" / "share" / "Anki2"
    source_media_path = Path("media")

    # Check if source media directory exists
    if not source_media_path.exists():
        print(f"Error: Source directory '{source_media_path}' not found.")
        print("Please run this script from the root of the project where the 'media' folder is located.")
        return

    # Check if Anki base directory exists
    if not anki_base_path.exists():
        print(f"Error: Anki directory '{anki_base_path}' not found.")
        return

    # Define excluded directory names based on the request
    excluded_names = {'logs', 'addons21', 'addons22', 'Anki2', 'txt', 'db', 'json'}

    # Find valid user profiles
    profiles = []
    for item in anki_base_path.iterdir():
        if item.is_dir() and item.name not in excluded_names:
            profiles.append(item)

    if not profiles:
        print("No valid Anki user profiles found.")
        return

    # Sort profiles alphabetically for consistent display
    profiles.sort(key=lambda x: x.name)

    # Display profiles with last modified date
    print("Available Anki Profiles:")
    print("-" * 50)
    for index, profile_path in enumerate(profiles, 1):
        # Get last modified time
        mod_time = os.path.getmtime(profile_path)
        date_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{index}. {profile_path.name:<20} (Last Modified: {date_str})")
    print("-" * 50)

    # Get user selection
    try:
        choice = input("Select the profile number to copy media to: ")
        selection_index = int(choice) - 1
        
        if selection_index < 0 or selection_index >= len(profiles):
            print("Invalid selection.")
            return
            
        selected_profile = profiles[selection_index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    # Define destination: collection.media inside the selected profile
    dest_media_path = selected_profile / "collection.media"
    
    # Create destination directory if it doesn't exist
    dest_media_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCopying files to: {dest_media_path}")
    print("Excluding .json files...")

    copied_count = 0
    skipped_count = 0
    error_count = 0

    # Walk through the source media directory
    for root, dirs, files in os.walk(source_media_path):
        for file in files:
            # Skip JSON files
            if file.lower().endswith('.json'):
                continue

            source_file = Path(root) / file
            
            # Copy directly to destination, flattening directory structure
            dest_file = dest_media_path / file

            try:
                # Check if file already exists to avoid overwriting/copying unnecessarily
                if not dest_file.exists():
                    shutil.copy2(source_file, dest_file)
                    print(f"Copied: {file}")
                    copied_count += 1
                else:
                    # Optional: Check if file is different? For now, just skip.
                    skipped_count += 1
            except Exception as e:
                print(f"Error copying {file}: {e}")
                error_count += 1

    print("-" * 50)
    print(f"Copy complete.")
    print(f"Copied: {copied_count}")
    print(f"Skipped (already exists): {skipped_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    main()
