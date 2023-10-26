debugOut = True

        
def dbout(*output):
    if debugOut == True:
        print(output ,sep="::")
