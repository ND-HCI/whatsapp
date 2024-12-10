import csv

# Load the CSV file into a list of dictionaries
CSV_FILE_PATH = "utils/get_recs_test.csv"

def load_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

PRODUCTS = load_csv(CSV_FILE_PATH)
