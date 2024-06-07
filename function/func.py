
def extractNumber(message):
        numbers = ''.join([char for char in message if char.isdigit()])
        return numbers 
