from hyperopt import hp
from GCExtract import GCExtract

#This file keeps global constants that we might want to optimize over in a hyperparamter search.


# Documentation for hyperopt and the distributions can be found here:
#  https://github.com/hyperopt/hyperopt/wiki/FMin

#This is a list of global constants.  We'll convert them to g later.
#Each global constant is a tuple of:
# (parameterName, distributionFn, distributionFnArgsExceptForLabel, fixedValue, varry=1)
gc=[]

###########
#Defining the global constants:

#Some examples:
#gc.append(('pastTimeBinsIncrementSec', hp.uniform, (1*60*60, 30*24*60*60), 60*60*24, 1))
#gc.append(('pastTimeNumBinsMax', hp.quniform, (1, 10*365, 1), 5*365, 0))
#gc.append(('variablesMakeStationary', hp.randint, (1,),  0, 0))
#gc.append(('spacyLanguageModel', hp.choice, (('en',),), 'en', 1))



#######################

#Produce g and searchSpace and other variables we will be importing from other files:
(g, searchVarNamesInOrder, fixedParamDict, searchSpace)=GCExtract(gc)
