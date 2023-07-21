import argparse
import fitz  # PyMuPDF
import os
import re
from PyPDF2 import PdfReader


def parse_text(text):
    # Define regular expressions to match the date
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')

    # Search for the date in the text
    date_match = date_pattern.search(text)

    # If a date is found, extract the three lines ending with the date
    if date_match:
        end = date_match.end()
        lines = text[:end].split('\n')
        date = lines[-1].replace('/', '-')
        employee_id = lines[-3]
        name = lines[-2].replace(' ', '-')
    else:
        date = 'unknown'
        employee_id = 'unknown'
        name = 'unknown'

    return date, employee_id, name


def split_pdf(file: str, directory: str):
    if not os.path.isfile(file):
        raise FileNotFoundError(f"Could not find file: {file}")
    if not os.path.isdir(directory):
        os.makedirs(directory)

    top_start = 0
    top_end = 0.48
    bottom_start = 0.46
    bottom_end = 0.93

    try:
        doc = fitz.open(file)
        reader = PdfReader(file)
        for i in range(len(doc)):
            page = doc[i]
            text = reader.pages[i].extract_text()

            rect = page.rect
            top_rect = fitz.Rect(rect.tl.x, rect.tl.y + rect.height * top_start, rect.br.x, rect.height * top_end)
            bottom_rect = fitz.Rect(rect.tl.x, rect.height * bottom_start, rect.br.x, rect.br.y * bottom_end)

            lines = text.split('\n')
            mid = len(lines) // 2
            top_text = '\n'.join(lines[:mid])
            bottom_text = '\n'.join(lines[mid:])
            top_date, top_id, top_name = parse_text(top_text)
            bottom_date, bottom_id, bottom_name = parse_text(bottom_text)

            top_pdf, bottom_pdf = fitz.open(), fitz.open()

            top_pdf.insert_pdf(doc, from_page=i, to_page=i)
            bottom_pdf.insert_pdf(doc, from_page=i, to_page=i)

            top_pdf[0].set_cropbox(top_rect)
            bottom_pdf[0].set_cropbox(bottom_rect)

            top_pdf.save(f'{directory}/payslip_{top_date}_{top_id}_{top_name}.pdf')
            bottom_pdf.save(f'{directory}/payslip_{bottom_date}_{bottom_id}_{bottom_name}.pdf')

    except Exception as e:
        print(f"Failed to split PDF: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split a PDF into individual payslips.')
    parser.add_argument('input_file', help='The path to the input PDF file.')
    parser.add_argument('output_directory', help='The path to the directory where the output files should be saved.')
    args = parser.parse_args()

    split_pdf(args.input_file, args.output_directory)
