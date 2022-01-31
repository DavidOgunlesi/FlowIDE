
import os

def readFileLines(filePath):
    arr = []
    with open(filePath) as my_file:
        for line in my_file:
            arr.append(line.replace("\n",""))
    return arr

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def dirExists(dir_path):
    directory = os.path.dirname(dir_path)
    return os.path.exists(directory)

def fileExists(file_path):
    return os.path.exists(file_path)