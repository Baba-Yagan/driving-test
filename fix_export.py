#!/usr/bin/env python3
import sys

def fix_anki_export(input_file, output_file):
    """
    Fix Anki export by converting Correct1/Correct2/Correct3 true/false values
    to a single CorrectChoice number (1, 2, or 3).
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process header lines (keep them as-is)
    header_lines = []
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('#'):
            header_lines.append(line)
            data_start = i + 1
        else:
            break
    
    # Process data lines
    fixed_lines = header_lines.copy()
    
    for line in lines[data_start:]:
        line = line.rstrip('\n')
        if not line.strip():  # Skip empty lines
            fixed_lines.append(line + '\n')
            continue
            
        fields = line.split('\t')
        
        # Expected field positions based on template.json:
        # 0:ID, 1:Category, 2:Number, 3:Question, 4:Image, 5:CorrectChoice, 
        # 6:Explanation, 7:DifficultyLevel, 8:Outdated, 9:Answer1, 10:Answer2, 11:Answer3,
        # 12:Correct1, 13:Correct2, 14:Correct3
        
        if len(fields) >= 15:  # Make sure we have all expected fields
            correct1 = fields[12].lower() == 'true'
            correct2 = fields[13].lower() == 'true'
            correct3 = fields[14].lower() == 'true'
            
            # Determine correct choice number
            if correct1:
                correct_choice = "1"
            elif correct2:
                correct_choice = "2"
            elif correct3:
                correct_choice = "3"
            else:
                correct_choice = "1"  # Default fallback
            
            # Set CorrectChoice field (position 5)
            fields[5] = correct_choice
            
            # Remove the last 3 fields (Correct1, Correct2, Correct3)
            fields = fields[:12]
            
            # Reconstruct the line
            fixed_line = '\t'.join(fields)
            fixed_lines.append(fixed_line + '\n')
        else:
            # If line doesn't have expected number of fields, keep as-is
            fixed_lines.append(line + '\n')
    
    # Write fixed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed export saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_export.py <input_file> <output_file>")
        print("Example: python fix_export.py export.txt export_fixed.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        fix_anki_export(input_file, output_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
