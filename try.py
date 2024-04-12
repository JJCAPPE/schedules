import os

def check_shell_config_files():
    print("Checking shell configuration files...")
    shell_config_files = ['~/.bash_profile', '~/.bashrc', '~/.zshrc']
    home = os.path.expanduser('~')
    for file_path in shell_config_files:
        file_path = os.path.join(home, file_path.lstrip('~'))
        print(f"Checking file: {file_path}")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                for line in file:
                    if 'PYTHONPATH' in line or 'PYTHONHOME' in line:
                        print(f"Environment variable pointing to Homebrew directory found in {file_path}:")
                        print(line.strip())
                        # You can choose to remove or update the line here
                    # You can add more checks for other environment variables if needed

def check_python_configs():
    print("Checking user-specific directories for Python configurations...")
    python_config_dirs = ['~/.config', '~/.local']
    home = os.path.expanduser('~')
    for dir_path in python_config_dirs:
        dir_path = os.path.join(home, dir_path.lstrip('~'))
        print(f"Checking directory: {dir_path}")
        if os.path.exists(dir_path):
            print(f"Python-specific configurations found in {dir_path}:")
            for root, _, files in os.walk(dir_path):
                for file_name in files:
                    if file_name.endswith('.py'):
                        file_path = os.path.join(root, file_name)
                        print(file_path)
                        # You can read and inspect the contents of Python configuration files here

# Check shell configuration files for environment variables
check_shell_config_files()

# Check user-specific directories for Python configurations
check_python_configs()


