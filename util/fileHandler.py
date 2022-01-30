
def readFileLines(filePath):
    arr = []
    with open(filePath) as my_file:
        for line in my_file:
            arr.append(line.replace("\n",""))
    return arr