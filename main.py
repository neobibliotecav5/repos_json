import os
import json
import fnmatch
import shutil

folder_path = r"C:\Users\Toshiba\Downloads\Compressed\whisper-main_repo"  # Replace with the desired path

limit = 1000  # Limit the number of lines to read per file

# Define common and modern image file extensions
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.heif', '.avif']

def is_image(file_path):
    """Check if a file is an image based on its extension."""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in image_extensions

def copy_image_to_output_dir(file_path, output_dir):
    """Copies an image file to the specified output directory."""
    destination = os.path.join(output_dir, os.path.basename(file_path))
    shutil.copy(file_path, destination)
    print(f"Copied image: {file_path} to {output_dir}")

def read_file_with_limit(file_path, line_limit=limit):
    """Reads a file up to a specific number of lines."""
    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if i >= line_limit:
                return lines, True
            lines.append(line)
    return lines, False

def read_gitignore(gitignore_path):
    """Reads a .gitignore file and returns a list of ignore patterns."""
    ignore_patterns = []
    with open(gitignore_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                ignore_patterns.append(line.strip())
    return ignore_patterns

def should_ignore(path, ignore_patterns):
    """Determines if a file or directory should be ignored."""
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def scan_directory(directory, ignore_patterns, output_dir):
    """Scans a directory and returns a list with the path and content of each file."""
    file_data = []
    index = {}
    ignored_files_count = 0
    binary_files_count = 0
    total_files_count = 0
    truncated_files = []

    for root, dirs, files in os.walk(directory):
        relative_root = os.path.relpath(root, directory)
        index[relative_root] = []

        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]

        for file in files:
            total_files_count += 1
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)  # Get relative path

            if should_ignore(file_path, ignore_patterns):
                ignored_files_count += 1
                continue

            index[relative_root].append(os.path.basename(file_path))

            if is_image(file_path):
                copy_image_to_output_dir(file_path, output_dir)
                file_data.append({"path": relative_path, "content": "Binary image file"})  # Use relative path
            else:
                try:
                    lines, truncated = read_file_with_limit(file_path)
                    if truncated:
                        truncated_files.append(relative_path)
                    file_data.append({"path": relative_path, "content": "".join(lines)})  # Use relative path
                except UnicodeDecodeError:
                    binary_files_count += 1
                    file_data.append({"path": relative_path, "content": "Cannot read binary file"})  # Use relative path
                except Exception as e:
                    file_data.append({"path": relative_path, "content": f"Error reading file: {e}"})  # Use relative path

    return file_data, index, total_files_count, ignored_files_count, binary_files_count, truncated_files

def main(folder_path, output_dir):
    gitignore_path = os.path.join(folder_path, '.gitignore')
    ignore_patterns = read_gitignore(gitignore_path) if os.path.exists(gitignore_path) else []

    file_data, index, total_files, ignored_files, binary_files, truncated_files = scan_directory(folder_path, ignore_patterns, output_dir)

    root_folder_name = os.path.basename(folder_path)  # Get only the folder name

    data = {
        "root": root_folder_name,  # Use only the folder name
        "index": index,  # Directory index
        "files": file_data
    }

    # Use the root folder name for the JSON file
    with open(os.path.join(output_dir, f'{root_folder_name}.json'), 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    print(f"Total files processed: {total_files}")
    print(f"Ignored files due to .gitignore: {ignored_files}")
    print(f"Binary or unreadable files: {binary_files}")
    if truncated_files:
        print(f"Truncated files (limited to {limit} lines):")
        for file in truncated_files:
            print(f" - {file}")

output_dir = r"G:\My Drive\Desarrollo de software\Repos a JSON\repos_json\output"  # Replace with your desired output directory

# Crear output_dir si no existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Run the script
main(folder_path, output_dir)