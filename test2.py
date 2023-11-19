import os
import json
import fnmatch
import shutil

folder_path = r"G:\My Drive\Libros\Zero to One\De zero a uno"  # Replace with the desired path
output_dir = r"G:\My Drive\Desarrollo de software\Repos a JSON\repos_json\x"  # Replace with your desired output directory

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
                if is_image(file_path):
                    copy_image_to_output_dir(file_path, output_dir)
                file_data.append({"path": file_path, "content": "Cannot read binary file"})
            except Exception as e:
                file_data.append({"path": file_path, "content": f"Error reading file: {e}"})

    return file_data, total_files_count, ignored_files_count, binary_files_count

def main(folder_path, output_dir):
    gitignore_path = os.path.join(folder_path, '.gitignore')
    ignore_patterns = read_gitignore(gitignore_path) if os.path.exists(gitignore_path) else []

    file_data, total_files, ignored_files, binary_files = scan_directory(folder_path, ignore_patterns, output_dir)

    data = {
        "root": folder_path,
        "files": file_data
    }

    with open(os.path.join(output_dir, 'output.json'), 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    print(f"Total files processed: {total_files}")
    print(f"Ignored files due to .gitignore: {ignored_files}")
    print(f"Binary or unreadable files: {binary_files}")

# Example usage
main(folder_path, output_dir)