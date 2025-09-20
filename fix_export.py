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
        
        # Actual field positions from your data:
        # 0:ID, 1:Category, 2:Deck, 3:Number, 4:CorrectChoice, 5:Question, 
        # 6-8:(Answer1,Answer2,Answer3), 9-11:(Correct1,Correct2,Correct3)
        
        # Find where the Correct1/Correct2/Correct3 fields are
        # They should be the last 3 non-empty fields, or we need to look for true/false values
        if len(fields) >= 13:  # Make sure we have enough fields
            # Look for true/false values in the last few fields
            correct_fields = []
            for i in range(len(fields) - 6, len(fields)):  # Check last 6 fields for true/false
                if i >= 0 and fields[i].lower() in ['true', 'false']:
                    correct_fields.append((i, fields[i].lower() == 'true'))
            
            if len(correct_fields) >= 3:  # Found the correct fields
                # Take the last 3 true/false fields as Correct1, Correct2, Correct3
                correct1_idx, correct1 = correct_fields[-3]
                correct2_idx, correct2 = correct_fields[-2] 
                correct3_idx, correct3 = correct_fields[-1]
                
                # Determine correct choice number
                if correct1:
                    correct_choice = "1"
                elif correct2:
                    correct_choice = "2"
                elif correct3:
                    correct_choice = "3"
                else:
                    correct_choice = "1"  # Default fallback
                
                # Set CorrectChoice field (position 4, which is the 5th column)
                fields[4] = correct_choice
                
                # Clear the Correct1, Correct2, Correct3 fields (keep tabs by using empty strings)
                fields[correct1_idx] = ""
                fields[correct2_idx] = ""
                fields[correct3_idx] = ""
                
                # Reconstruct the line
                fixed_line = '\t'.join(fields)
                fixed_lines.append(fixed_line + '\n')
            else:
                # No true/false fields found, keep line as-is
                fixed_lines.append(line + '\n')
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
