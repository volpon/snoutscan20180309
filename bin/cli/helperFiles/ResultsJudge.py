import numpy as np

def ResultsJudge(confusionMatrix):
    '''
    This function calculates the percentage of images correctly matched from a pandas confusion 
    matrix as output by SSMatchAll.
    
    Inputs:
        confusionMatrix - A confusion matrix summarizing the results.
    '''
    
    #Sum the diagonal
    numCorrect=np.trace(confusionMatrix)
    numTried=np.sum(np.sum(confusionMatrix))
    
    if numTried>0:
        percentCorrect=numCorrect/numTried
    else:
        percentCorrect=0
 
    return percentCorrect