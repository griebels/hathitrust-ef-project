#!/usr/bin/env python3
import re
import csv
import argparse
import sys
import os

def format_text(text):
    """
    Clean OCR text formatting by:
    1. Preserving paragraph breaks (multiple newlines)
    2. Removing artificial line breaks within sentences
    """
    if not text:
        return text

    text = str(text)
    text = re.sub(r'\n{2,}', 'PARAGRAPH_BREAK', text)
    text = text.replace('\n', ' ')
    text = text.replace('PARAGRAPH_BREAK', '\n\n')
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def process_text_to_csv(text_content, output_filename):
    """
    Function to process a downloaded fulltext HT book from txt file. The txt file 
    contains page separators in format ## p. (#1) ####################### 
    
    This function converts the file to csv format, with columns for pages (HT sequence),
    original OCR text, and cleaned text formatting.
    """
    separator_pattern = r'## p\.? ([^(#]*)\(#(\d+)\) #{30,}'
    separators = list(re.finditer(separator_pattern, text_content))

    if not separators:
        return "Error: No page separators found in the text file. Check the format."

    page_data = []

    for i in range(len(separators)):
        current_separator = separators[i]
        page_number = current_separator.group(2)  # To capture the sequence page number (in parentheses)
        
        start_pos = current_separator.end()
        end_pos = separators[i+1].start() if i < len(separators) - 1 else len(text_content)

        page_content = text_content[start_pos:end_pos].strip()
        cleaned_content = format_text(page_content)

        page_data.append((page_number, page_content, cleaned_content))

    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['page', 'text', 'clean_text'])  
            for page_num, original_text, cleaned_text in page_data:
                csv_writer.writerow([page_num, original_text, cleaned_text])
        
        return f"CSV file created successfully: {output_filename} with {len(page_data)} pages"
    except Exception as e:
        return f"Error writing CSV file: {str(e)}"

def main():
    parser = argparse.ArgumentParser(
        description='Process a text file with page separators and convert to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example separator format:
            ## p. xiv (#20) #############################################

            The script extracts the page number (20), the associated OCR text, and a cleaned version.
        """
    )
    
    parser.add_argument('input_file', help='Path to the input text file to process')
    parser.add_argument('-o', '--output', default=None, 
                        help='Path for the output CSV file (default: input_filename.csv)')
    
    args = parser.parse_args()

    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        args.output = f"{base_name}.csv"
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as file:
            text_content = file.read()
        
        result = process_text_to_csv(text_content, args.output)
        print(result)
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
