import os

copyright_str = """Copyright (C) 2021-2022 Simon Ma <https://github.com/SiiiMiii> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
copyright_text = '''"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/SiiiMiii> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
'''
msg_lines = len(copyright_str.split("\n"))

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, _, files in os.walk(directory):
        for file in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, file)
            if file.endswith(".py"):
                file_paths.append(filepath)  # Add it to the list.

    return file_paths
 
all_file_paths = get_filepaths(".")
all_file_paths = ["main.py"]
# print(all_file_paths)

def write_copyright_msg():
    for filepath in all_file_paths:
        with open(filepath, "r+") as f:
            print("".join(f.readlines()[1:msg_lines]))
            print(copyright_str)

            if "".join(f.readlines()[1:msg_lines]) == copyright_str:
                print("YEHAA")
                continue
            
            # content = f.read()
            # f.seek(0, 0)
            # f.write('"""\n' + copyright_str + '"""'+ content)
write_copyright_msg()
