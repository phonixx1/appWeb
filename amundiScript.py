import pandas as pd
from numpy import nan

def sign(x):
    """
    We will use this function to work with the sign of cumul return without put a lot of cond if/else to check the sign
    """
    if x == 0:
        return 0
    return -1 if x < 0 else 1


def genDrawUpDrawDown(dfReturns, triger=0.2):
    """
    Generation of draw up and draw down from a time series of returns
    Param : dfReturns => a data frame of returns ( without NaN remplace them by 0)
            triger => minimum variation threshold, float number set at 0.2=20% by default
    Returns : PositiveCumReturn
              NegativeCumReturn
    """
    returnsArray = list(dfReturns)
    n = len(returnsArray)

    if n == 0:
        return [],[]

    cumulReturnsArray = [nan]*n
    positiveCumReturn = []
    negativeCumReturn = []

    cumulReturnsArray[0] = returnsArray[0]
    index = 0

    # will be a n-complexity even if we have several loop because in each loop we increase the same index
    while index + 1 < n:
        # search for a draw-down or draw-up by cumulating the returns
        if abs(cumulReturnsArray[index]) < triger:
            cumulReturnsArray[index + 1] = ((1 + returnsArray[index + 1])*(1 + cumulReturnsArray[index]) - 1)
            index += 1
        else:
            # indexExtremum will be the index of the beginning of the movement
            indexExtremum = index

            # stopTriger will be our stop condition if we exceed our trigger again
            stopTriger = returnsArray[index + 1]

            # upOrDown = 1 -> draw-up ; upOrDown = -1 -> draw-down
            upOrDown = sign(cumulReturnsArray[index])

            # we accumulate returns as long as we don't exceed the trigger
            while upOrDown * stopTriger > -triger:
                cumulReturnsArray[index + 1] = ((1 + cumulReturnsArray[index]) * (1 + returnsArray[index + 1]) - 1)
                index += 1

                # if we have a new max (resp. min) in our draw-up (resp. draw-down)
                if upOrDown * stopTriger > 0:
                    indexExtremum = index
                    stopTriger = returnsArray[index+1]

                # else accumulate returns
                else:
                    stopTriger = (1 + stopTriger) * (1 + returnsArray[index + 1]) - 1

                if index >= n-2:
                    indexExtremum = n-2
                    break
            # Extend PositiveCumReturn and NegativeCumReturn with the new draw-up/draw-down
            nTemp = len(positiveCumReturn)
            positiveCumReturn.extend(sign(1 + upOrDown) * cumulReturnsArray[nTemp:indexExtremum + 1] + [nan] * (indexExtremum + 1 - nTemp) * sign(1 - upOrDown))
            negativeCumReturn.extend(sign(1 - upOrDown) * cumulReturnsArray[nTemp:indexExtremum + 1] + [nan] * (indexExtremum + 1 - nTemp) * sign(1 + upOrDown))

            # Incrementation for the next loop
            cumulReturnsArray[indexExtremum+1] = returnsArray[indexExtremum + 1]
            index = indexExtremum + 1

    upOrDown = sign(cumulReturnsArray[index])
    cumulReturnsArray[n-1] = (1 + cumulReturnsArray[n-2]) * (1 + returnsArray[n-1]) - 1
    positiveCumReturn.extend(sign(1 + upOrDown) * [cumulReturnsArray[n-1]] + [nan] * sign(1 - upOrDown))
    negativeCumReturn.extend(sign(1 - upOrDown) * [cumulReturnsArray[n-1]] + [nan] * sign(1 + upOrDown))

    return positiveCumReturn, negativeCumReturn
