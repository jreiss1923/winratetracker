def calculateWinRate(currentRecord, goingToGo, desiredWinRate):
    recordArr = currentRecord.split('-')

    totalWins = int(recordArr[0])
    totalLosses = int(recordArr[1])

    goingToGoArr = goingToGo.split('-')

    goingToWin = int(goingToGoArr[0])
    goingToLose = int(goingToGoArr[1])

    desiredDecimal = desiredWinRate/100

    if(goingToWin/(goingToWin + goingToLose) <= desiredDecimal):
        raise ValueError("Your desired winrate is greater than or equal to the record you need to go.")

    numberToGo = int(round((totalWins - totalWins * desiredDecimal - totalLosses * desiredDecimal)/(desiredDecimal * goingToWin + desiredDecimal * goingToLose - goingToWin), 0))
    print("\n\nYou need to go " + str(goingToGo) + " " + str(numberToGo) + " more times to reach your desired winrate of " + str(desiredWinRate) + "%.")

# example usage: calculateWinRate("151-322", "2-2", 32.5)
# output: "You need to go 2-2 4 more times to reach your desired winrate of 32.5%."




