import os

base_dir = "included_studies_sorted"
output_file = "included_studies_file_list.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for root, dirs, files in os.walk(base_dir):
        f.write(f"\nDirectory: {root}\n")
        for file in files:
            f.write(f"  {file}\n")

print("File list saved to included_studies_file_list.txt")
