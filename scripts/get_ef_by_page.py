#!/usr/bin/env python3
import requests
import csv
import os
import argparse
import sys


def process_htid(htid, output_dir=None):
    """
    This function processes an HTID and creates a csv with pages (based on sequence numbers)
    and extracted features for each page.
    
    Args:
        htid (str): the HTID to process
        
    Returns:
        str: Path to the created CSV file or error message
    """
    base_url = "https://data.htrc.illinois.edu/ef-api/volumes/"
    
    url = f"{base_url}{htid}/pages"
    
    # Create output directory 
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = f"{htid.replace('/', '_')}.csv"
    if output_dir:
        output_file = os.path.join(output_dir, output_file)
    
    try:
        # GET request for the API
        print(f"Sending request to {url}")
        response = requests.get(url)
        
        # Check if successful
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', {}).get('pages', [])
            
            with open(output_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['page', 'words_pos'])
                for page in pages:
                    seq = page.get('seq')
                    body = page.get('body')
                    
                    if body is not None:
                        token_pos_count = body.get('tokenPosCount')
                        writer.writerow([seq, token_pos_count])
                    else:
                        writer.writerow([seq, 'No body data'])
            
            return f"Successfully processed {htid} and saved to {output_file}"
        else:
            return f"Failed to retrieve data for {htid}: {response.status_code}"
    except Exception as e:
        return f"Error processing {htid}: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='Process an HTID and create a csv file with pages and extracted features.')
    parser.add_argument('htid', help='The HathiTrust ID to process')
    parser.add_argument('-o', '--output-dir', help='Directory to save output file (default: current directory)')
    
    args = parser.parse_args()
    
    result = process_htid(args.htid, output_dir=args.output_dir)
    
    # Print the result (optional)
    print(result)


if __name__ == "__main__":
    main()