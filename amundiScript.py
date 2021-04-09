import pandas as pd
import time
from numpy import nan
import sys

if len(sys.argv) != 1:
    exit(1)

FILE_PATH = "SPX.csv" # Put the path of your data


def sign(x):
    """
    We will use this function to work with the sign of cumul return without put a lot of cond if/else to check the sign
    """
    if x == 0:
        return 0
    return -1 if x < 0 else 1


def gen_draw_up_draw_down(dfReturns, triger=0.2):
    """
    Generation of draw up and draw down from a time series of returns
    Param : dfReturns => a data frame of returns ( without NaN remplace them by 0)
            triger => minimum variation threshold, float number set at 0.2=20% by default
    Returns : PositiveCumReturn
              NegativeCumReturn
    """
    returnsArray = list(dfReturns) # We will loop so it's better to work with array than df
    cumulReturnsArray = [returnsArray[0]]

    PositiveCumReturn = []
    NegativeCumReturn = []

    n = len(returnsArray)
    index = 0

    # will be a n-complexity even if we have several loop because in each loop we increase the same index
    while index + 1 < n:
        if abs(cumulReturnsArray[index]) < triger: # search for a draw-down or draw-up by cumulating the returns
            cumulReturnsArray.append((1 + returnsArray[index + 1])*(1 + cumulReturnsArray[index]) - 1)
            index += 1
        else:
            # indexExtremum will be the index of the beginning of the movement
            indexExtremum = index

            # stopTriger will be our stop condition if we exceed our trigger again
            stopTriger = returnsArray[index + 1]

            # upOrDown = 1 => draw-up ; upOrDown = -1 => draw-down
            upOrDown = sign(cumulReturnsArray[index])

            # we accumulate returns as long as we don't exceed the trigger
            while upOrDown * stopTriger > -triger:
                cumulReturnsArray.append((1 + cumulReturnsArray[index]) * (1 + returnsArray[index + 1]) - 1)
                index += 1
                if index >= n-2:                                          
                    indexExtremum = n-2
                    break

                # if we have a new max (resp. min) in our draw-up (resp. draw-down)
                if upOrDown * stopTriger > 0:
                    indexExtremum = index
                    stopTriger = returnsArray[index+1]
                else:                                                      # else accumulate returns
                    stopTriger = (1 + stopTriger) * (1 + returnsArray[index + 1]) - 1

            cumulReturnsArray = cumulReturnsArray[:indexExtremum + 1]

            # Extend PositiveCumReturn and NegativeCumReturn with the new draw-up/draw-down
            nTemp = len(PositiveCumReturn)
            PositiveCumReturn.extend(sign(1 + upOrDown) * cumulReturnsArray[nTemp:] + [nan] * (indexExtremum + 1 - nTemp) * sign(1 - upOrDown))
            NegativeCumReturn.extend(sign(1 - upOrDown) * cumulReturnsArray[nTemp:] + [nan] * (indexExtremum + 1 - nTemp) * sign(1 + upOrDown))

            # Incrementation for the next loop
            cumulReturnsArray.append(returnsArray[indexExtremum+1])
            index=indexExtremum+1

    cumulReturnsArray[n-1] = (1+cumulReturnsArray[n-2]) * (1+returnsArray[n-1]) - 1
    PositiveCumReturn.append(cumulReturnsArray[n-1])
    NegativeCumReturn.append(nan)

    return PositiveCumReturn, NegativeCumReturn


if __name__ == '__main__':
    start_time = time.time()
    data = pd.read_csv(FILE_PATH, sep=',')
    # Percentage change between the current and a prior element and replace NaN by 0.
    data["returns"] = data["price"].pct_change().fillna(0)
    i = 0
    while i < 1:
        PositiveCumReturn, NegativeCumReturn = gen_draw_up_draw_down(data["returns"])
        i += 1
    print("--- %s seconds ---" % (time.time() - start_time))
