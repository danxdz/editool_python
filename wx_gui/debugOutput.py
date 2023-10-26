debugOut = True

class debugOut:
        
    def print(*output):
        if debugOut == True:
            print(output ,sep="::")
