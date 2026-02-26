import json
import os
import glob

# Folder containing JSON files
input_folder = "media"
output_file = "output.tsv"

# TSV Header
header = [
    "id", "questionText", "explanationNote", "mediaContent",
    "answer1", "answer2", "answer3",
    "is-correct-answer-1", "is-correct-answer-2", "is-correct-answer-3", "tags"
]

# Helper function to safely extract and clean string values
def safe_get(value):
    if value:
        return str(value).replace("\t", " ").replace("\n", " ").strip()
    return ""

# Helper function to convert media filenames to HTML embeds
def format_media(filename):
    if not filename:
        return ""
    # os.path.basename is used here for safety, though filename should already be clean
    clean_filename = os.path.basename(filename)
    if clean_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
        return f'<img src="{clean_filename}" alt="{clean_filename}">'  # Image embed
    elif clean_filename.lower().endswith(('.mp4', '.gif')):
        return f'[sound:{clean_filename}]'  # Custom video embed
    return f'<a href="{clean_filename}">{clean_filename}</a>'  # Other media link

# Process JSON files
rows = []

# CHANGE: Updated glob pattern to search inside subdirectories created by generator.py
# generator.py creates media/question_{id}/question.json
search_pattern = os.path.join(input_folder, "*/question.json")

for file in glob.glob(search_pattern):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    q_id = safe_get(data.get("id"))
    question_text = safe_get(data.get("questionText"))
    explanation_note = safe_get(data.get("explanationNote"))

    # Extract question media filename safely
    media_data = data.get("mediaContent")
    media_content = ""
    
    if isinstance(media_data, dict):
        # CHANGE: Use printMediaName if available, as generator.py uses it to save the file
        filename = media_data.get("printMediaName")
        if not filename:
            # Fallback to extracting from URL
            media_url = media_data.get("mediaUrl")
            if media_url:
                filename = os.path.basename(media_url)
        
        if filename:
            media_content = format_media(filename)

    # Extract answers
    answers = data.get("questionAnswers", [])
    answer_texts = []
    correct_answers = []

    for a in answers:
        text = safe_get(a.get("answerText"))
        
        # Handle answer media
        a_media_data = a.get("mediaContent")
        a_media_filename = ""
        
        if isinstance(a_media_data, dict):
            # CHANGE: Use printMediaName for answers as well
            a_media_filename = a_media_data.get("printMediaName")
            if not a_media_filename:
                a_media_url = a_media_data.get("mediaUrl")
                if a_media_url:
                    a_media_filename = os.path.basename(a_media_url)
        
        if a_media_filename:
            text = f'{format_media(a_media_filename)} {text}'
            
        answer_texts.append(text)
        correct_answers.append("true" if a.get("isCorrect") else "false")

    # Ensure exactly 3 answers (fill empty slots with a tab)
    while len(answer_texts) < 3:
        answer_texts.append("")
        correct_answers.append("false")

    # Convert to TSV row (ensure correct tabbing)
    row = [
        q_id, question_text, explanation_note, media_content,
        answer_texts[0], answer_texts[1], answer_texts[2],
        correct_answers[0], correct_answers[1], correct_answers[2], ""
    ]
    rows.append("\t".join(row))

# Write to TSV
with open(output_file, "w", encoding="utf-8") as f:
    f.write("#separator:tab\n#html:true\n#tags column:11\n")
    f.write("\t".join(header) + "\n")
    for row in rows:
        f.write(row + "\n")

print(f"TSV file saved to {output_file}")
