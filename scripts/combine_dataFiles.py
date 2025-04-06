#!/usr/bin/env python3
import pandas as pd
import numpy as np
import argparse
import os

def combine_csv_files(file1, file2, output_filename):
    """
    Function to combine the two CSV files based on the 'page' column (this column must exist in
    both files for this function to work).
    The second file (extracted features file) has "No page data" replaced with blank cells.

    The order of files is important here -- the EF csv file should be listed second.
    
    Args:
        file1 (str): Path to the preprocessed dataset CSV (created from preprocessing a fulltext
        HathiTrust txt file.)
        file2 (str): Path to the extracted features CSV (created with the EF API)
        output_filename (str): Path to save the combined CSV.

    Returns:
        str: Success message.
    """
    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except Exception as e:
        return f"Error reading input files: {e}"

    # Replace "No body data" with blank cells in file2 (extracted features file)
    non_page_cols = [col for col in df2.columns if col != 'page']
    for col in non_page_cols:
        df2[col] = df2[col].replace("No body data", np.nan)

    # This part renames columns with the same name from different csv files (other than the
    # page column, which is what we're joining on). This is mostly a safety measure in case
    # I change something in the previous scripts and forget.
    cols1 = [col for col in df1.columns if col != 'page']
    cols2 = non_page_cols

    if len(set(cols1 + cols2)) < len(cols1 + cols2):  
        if len(cols1) > 0:
            df1.rename(columns={cols1[0]: f"file1_{cols1[0]}"}, inplace=True)
            cols1 = [f"file1_{cols1[0]}"]
        if len(cols2) > 0:
            df2.rename(columns={cols2[0]: f"file2_{cols2[0]}"}, inplace=True)
            cols2 = [f"file2_{cols2[0]}"]


    merged_df = pd.merge(df1, df2, on='page', how='outer')

    try:
        merged_df['page'] = pd.to_numeric(merged_df['page'])
        merged_df.sort_values('page', inplace=True)
    except:
        merged_df.sort_values('page', inplace=True)

    try:
        merged_df.to_csv(output_filename, index=False)
        return f"Combined CSV file created successfully: {output_filename}"
    except Exception as e:
        return f"Error writing output file: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Combine preprocessed CSV and extracted features CSV into one file."
    )
    parser.add_argument('file1', help='Path to preprocessed dataset CSV')
    parser.add_argument('file2', help='Path to extracted features CSV')
    parser.add_argument('-o', '--output', default=None, help='Path for output CSV file')

    args = parser.parse_args()

    if args.output is None:
        base1 = os.path.splitext(os.path.basename(args.file1))[0]
        base2 = os.path.splitext(os.path.basename(args.file2))[0]
        args.output = f"{base1}_{base2}_combined.csv"

    result = combine_csv_files(args.file1, args.file2, args.output)
    print(result)

if __name__ == '__main__':
    main()
