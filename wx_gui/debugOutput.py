debugOut = True

def debug(*output):
    if debugOut == True:
        print(output ,sep="::")
