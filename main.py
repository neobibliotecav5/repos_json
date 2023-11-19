import os
import json
import fnmatch

folder_path = r"C:\Users\Toshiba\Downloads\Compressed\whisper-main"  # Replace with the desired path

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

def scan_directory(directory, ignore_patterns):
    """Scans a directory and returns a list with the path and content of each file."""
    file_data = []
    ignored_files_count = 0
    binary_files_count = 0
    total_files_count = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]

        for file in files:
            total_files_count += 1
            file_path = os.path.join(root, file)
            if should_ignore(file_path, ignore_patterns):
                ignored_files_count += 1
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_data.append({"path": file_path, "content": content})
            except UnicodeDecodeError:
                binary_files_count += 1
                file_data.append({"path": file_path, "content": "Cannot read binary file"})
            except Exception as e:
                file_data.append({"path": file_path, "content": f"Error reading file: {e}"})

    return file_data, total_files_count, ignored_files_count, binary_files_count

def main(folder_path):
    gitignore_path = os.path.join(folder_path, '.gitignore')
    ignore_patterns = read_gitignore(gitignore_path) if os.path.exists(gitignore_path) else []

    file_data, total_files, ignored_files, binary_files = scan_directory(folder_path, ignore_patterns)

    data = {
        "root": folder_path,
        "files": file_data
    }

    with open('output.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    print(f"Total files processed: {total_files}")
    print(f"Ignored files due to .gitignore: {ignored_files}")
    print(f"Binary or unreadable files: {binary_files}")

# Example usage
main(folder_path)