def verify_csv_integrity(file_path):
    expected_comma_count = None

    with open(file_path, 'r') as file:
        for idx, line in enumerate(file):
            # Count the number of commas in the line (i.e., columns)
            comma_count = line.count(',')

            # If it's the first line, set expected column count
            if idx == 0:
                expected_comma_count = comma_count

            # If any other line doesn't have the expected number of commas, print an error
            if comma_count != expected_comma_count:
                print(f"Error at Line {idx + 1}: Expected {expected_comma_count} commas, but found {comma_count}")
                print(f"Problematic Row: {line.strip()}")
                return False

    print("File integrity verified successfully!")
    return True


# Example usage:
file_path = "Chase0106_Activity_20250205.CSV"
if verify_csv_integrity(file_path):
    print("File is ready for processing.")
else:
    print("File has integrity issues. Please check the logs above.")
