
# File Manager (FM)
#   For reading from, writing, or appending to files


# NonLocal Modules
import os
import hashlib
import pickle

# Returns all lines
#  Must pass file ext along as path
def get_all(path):
    with open(path, 'r') as f:
        objects = f.readlines()
        for i in range(0, len(objects)):
            objects[i] = objects[i][:-1]
        return objects

# Returns file as string
def get_string(path):
    with open(path, 'r') as f:
        return f.read().replace('\n', '')

# Returns a line with respect to index
def get_line(path, index):
    with open(path, 'r') as f:
        content = f.readlines()
        return content[index][:-1]

# Returns index of the first line to match a substring parameter
def get_index(path, substring):
    with open(path, 'r') as f:
        content = f.readlines()
        for i in range(0, len(content)):
            if substring == content[i]:
                return i
        return -1

# Appends a new line to a file
def append_line(path, string, endline='\n'):
    with open(path, 'a') as f:
        f.write(string + endline)

# Replaces line at index contents with string
def edit_line(path, index, string):
    with open(path, 'r') as rf:
        entire = rf.read()
        file_len = file_length(path)
        if index < file_len:
            start, end = index_position(entire, index)
            with open(path, 'w') as wf:
                wf.write(entire[:start] + str(string) + entire[end:])
        else:
            if file_exists(path):
                with open(path, 'a') as af:
                    for i in range(0, index - file_len):
                        af.write('\n')
                    af.write(string+'\n')
            else:
                print('ERROR: ' + path + ' does not exist')

# Return the contents of a line while removing that line from the file
def file_pop(path, index):
    item = ''
    with open(path, 'r') as rf:
        entire = rf.read()
        start, end = index_position(entire, index)
        with open(path, 'w') as wf:
            item = entire[start:end]
            wf.write(entire[:start-1] + entire[end:])
    return item
# - - - - - - - - - - - - - - - - - - - - - - -  #

def write_pickle(file_path, obj):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)

def get_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

# ---------------------------------------------- #

# Delete an entire file
def remove_file(path):
    os.remove(path)

# Delete an entire directory along with it's sub-file structure
def remove_directory(ndir):
    os.remove(ndir)

# Create a file if it does not already exist
#def create_file(path):


# Create a directory if it does not already exist
def create_directory(ndir):
    if not os.path.exists(ndir):
        os.makedirs(ndir)

# List all files and folders inside of the current directory
def list_all():
    names = []
    for name in os.listdir('.'):
        names.append(name)
    return names

# List all directories
def list_directories():
    #With respect to current directory, returns
    #a list of all subdirectories
    directories = []
    for name in os.listdir('.'):
        if os.path.isdir(name):
            directories.append(name)
    return directories

# List all files
def list_files(ext=''):
    files = []
    if len(ext) > 0 and ext[0] == '.':
        ext = ext[1:]
    for name in os.listdir('.'):
        if os.path.isfile(name):
            if len(ext) > 0:
                if name.endswith('.'+ext):
                    files.append(name)
            else:
                files.append(name)
    return files

# Return the number of lines in a file
def file_length(path):
   with open(path, 'r') as f:
       return len(f.readlines())

# ---------------------------------------------- #

def file_exists(path):
    for file in list_files():
        if file == path:
            return True
    return False

# ---------------------------------------------- #

# Changes directory (mimics terminal's cd)
def change_directory(ndirectory):
    os.chdir(ndirectory)

# Returns the return path given a path and current directory
def return_path(path, stay=False):
    start = 0
    return_path = ''
    for i in range(0, len(path)):
        if path[i] == '/':
            if len(path[start:i]) == 0:
                continue
            elif path[start:i] == '..':
                return_path = current_directory()+'/' + return_path
                os.chdir('../')
            else:
                os.chdir(path[start:i]+'/')
                return_path = '../' + return_path
            start = i+1
    if stay == False:
        os.chdir(return_path)
    return return_path

# Returns current parent directory
def current_directory():
    dir_path = dir_path = os.getcwd()
    end = len(dir_path)
    if dir_path[-1] == '/':
        end -= 1
    for i in range(2, len(dir_path)+1):
        if dir_path[-i] == '/':
            return dir_path[-i+1:end]
    return dir_path[:end]

# ---------------------------------------------- #

# Return index of text among potentially multiple lines
def index_position(text, index):
	#Returns the position(index1:index2) of an index
	count = 0
	start = 0
	end = 0
	for i in range(0, len(text)):
		if text[i] == '\n':
		# '\n' is a single character
			if count == index:
				end = i
				return start, end
			count += 1
			if count == index:
				start = i + 1
	return -1

# ---------------------------------------------- #

# Create a hash with respect to an excel file's string contents
def get_hash(path):
    content = ''
    lines = get_all(path)
    for i in range(0,len(lines)):
        content += lines[i]
        content += '~/'
    hash_object = hashlib.sha1(content.encode())
    hex_dig = hash_object.hexdigest()
    return str(hex_dig)
