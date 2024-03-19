from pathlib import Path
from titlecase import titlecase
from rich.console import Console
import re

def list_files(directory):
    try:
        directory_path = Path(directory)
        files = [entry.name for entry in directory_path.iterdir() if entry.is_file()]
        files.remove('templates.csv')
        return files
    except FileNotFoundError:
        print(f"The directory {directory} was not found.")
        return []

def separate_numbers(s):
    match = re.match(r"^(.*?)(\d+)$", s)
    if match:
        non_numeric, numeric = match.groups()
        return non_numeric, numeric
    else:
        return s, None

def split_type(header):
    search = re.search(r'((?:\w+\s?)+)\((@\w+)\)', header)
    if search:
        title, type_ = search.groups()
        return title, f'({type_})'
    return None, None

def file_name_to_title(file_name):
    name = file_name.rsplit('.', 1)[0].replace('_',' ')
    title = titlecase(name)
    return title

def error_msg_retry(msg):
      console = Console()
      console.print(f'[italic][bright_red]{msg}, try again[bright_red][/italic]')

def error_msg(msg):
      console = Console()
      console.print(f'[italic][bright_red]{msg}[bright_red][/italic]')

def unstyle(str):
    return re.sub(r'\[/?\w+\]', '', str)


