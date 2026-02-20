#!/usr/bin/env python3
"""
Script to create a clean zip file of the codebase for sharing.
Excludes: venv, __pycache__, .env files, .git, and other unnecessary files.
"""
import os
import zipfile
from pathlib import Path
from datetime import datetime

# Directories and files to exclude
EXCLUDE_DIRS = {
    'venv',
    '__pycache__',
    '.git',
    '.pytest_cache',
    '.mypy_cache',
    'node_modules',
    '.idea',
    '.vscode',
    'dist',
    'build',
    '*.egg-info'
}

EXCLUDE_FILES = {
    '.env.local',
    '.env',
    '.DS_Store',
    '*.pyc',
    '*.pyo',
    '*.log',
    '.python-version',
    '*.swp',
    '*.swo',
    '*~'
}

EXCLUDE_PATTERNS = [
    '**/__pycache__/**',
    '**/*.pyc',
    '**/.DS_Store',
    '**/.env*',
    '**/venv/**',
    '**/.git/**',
]

def should_exclude(path: Path, root: Path) -> bool:
    """Check if a file/directory should be excluded."""
    rel_path = path.relative_to(root)
    
    # Check if any part of the path matches exclude dirs
    for part in rel_path.parts:
        if part in EXCLUDE_DIRS:
            return True
        if part.startswith('.') and part != '.gitignore':
            if part not in ['.env.example']:  # Allow .env.example
                return True
    
    # Check file extensions
    if path.is_file():
        if path.suffix in ['.pyc', '.pyo', '.log', '.swp', '.swo']:
            return True
        if path.name in EXCLUDE_FILES:
            return True
        if path.name.startswith('.env') and path.name != '.env.example':
            return True
    
    # Check patterns
    path_str = str(rel_path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.replace('**/', '').replace('/**', '') in path_str:
            return True
    
    return False

def create_clean_zip(source_dir: Path, output_zip: Path):
    """Create a clean zip file excluding unnecessary files."""
    print(f"Creating clean zip from: {source_dir}")
    print(f"Output: {output_zip}")
    print("\nExcluding:")
    print("  - venv/")
    print("  - __pycache__/")
    print("  - .env.local, .env")
    print("  - .git/")
    print("  - *.pyc, *.log files")
    print()
    
    files_added = 0
    files_excluded = 0
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
            
            # Add files
            for file in files:
                file_path = root_path / file
                
                if should_exclude(file_path, source_dir):
                    files_excluded += 1
                    continue
                
                # Add file to zip
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
                files_added += 1
                if files_added % 50 == 0:
                    print(f"  Added {files_added} files...", end='\r')
    
    print(f"\n\nComplete!")
    print(f"  Files added: {files_added}")
    print(f"  Files excluded: {files_excluded}")
    print(f"\nZip file created: {output_zip}")
    print(f"Size: {output_zip.stat().st_size / 1024 / 1024:.2f} MB")

def main():
    """Main function."""
    # Get the project root (directory where script is located)
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"support_ticket_system_clean_{timestamp}.zip"
    output_path = project_root / output_name
    
    # Confirm
    print("=" * 60)
    print("  CREATE CLEAN ZIP FOR SHARING")
    print("=" * 60)
    print(f"\nProject root: {project_root}")
    print(f"Output file: {output_path}")
    print()
    
    # Check if output already exists
    if output_path.exists():
        response = input(f"{output_name} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        output_path.unlink()
    
    # Create the zip
    try:
        create_clean_zip(project_root, output_path)
        print("\n" + "=" * 60)
        print("SUCCESS! Your clean zip file is ready to share.")
        print("=" * 60)
    except Exception as e:
        print(f"\nERROR: {e}")
        if output_path.exists():
            output_path.unlink()
        raise

if __name__ == "__main__":
    main()

