from hyperopt import hp
from GCExtract import GCExtract
import cv2

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


#This flag defines if we load (and thus process) our images as color iamges or grayscale images:
gc.append(('colorNotGrayscale', hp.choice, ((cv2.IMREAD_GRAYSCALE, cv2.IMREAD_COLOR),), 
           cv2.IMREAD_GRAYSCALE, 1))

#The height that we convert all of the snout images to before we start the rest of the process:
#We keep the aspect ratio the same.
gc.append(('imgHeight', hp.quniform, (500,4096,1), 1000, 1))

#How many features to create for each image, maximum:
gc.append(('numFeaturesMax', hp.quniform, (500,20000,1), 8000, 1))




#######################

#Produce g and searchSpace and other variables we will be importing from other files:
(g, searchVarNamesInOrder, fixedParamDict, searchSpace)=GCExtract(gc)