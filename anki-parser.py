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
def format_media(media_url):
    if not media_url:
        return ""
    filename = os.path.basename(media_url)
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
        return f'<img src="{filename}" alt="{filename}">'  # Image embed
    elif filename.lower().endswith(('.mp4', '.gif')):
        return f'[sound:{filename}]'  # Custom video embed
    return f'<a href="{filename}">{filename}</a>'  # Other media link

# Process JSON files
rows = []
for file in glob.glob(os.path.join(input_folder, "*.json")):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    q_id = safe_get(data.get("id"))
    question_text = safe_get(data.get("questionText"))
    explanation_note = safe_get(data.get("explanationNote"))

    # Extract question media filename safely
    media_data = data.get("mediaContent")
    media_url = media_data.get("mediaUrl") if isinstance(media_data, dict) else None
    media_content = format_media(media_url)

    # Extract answers
    answers = data.get("questionAnswers", [])
    answer_texts = []
    correct_answers = []

    for a in answers:
        text = safe_get(a.get("answerText"))
        media = a.get("mediaContent", {}).get("mediaUrl") if isinstance(a.get("mediaContent"), dict) else None
        if media:
            text = f'{format_media(media)} {text}'  # Prepend media HTML embed
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
