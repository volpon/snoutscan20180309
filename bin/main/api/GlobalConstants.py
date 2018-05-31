from hyperopt import hp
from GCExtract import GCExtract

#This file keeps global constants that we might want to optimize over in a hyperparamter search.


# Documentation for hyperopt and the distributions can be found here:
#  https://github.com/hyperopt/hyperopt/wiki/FMin

#This is a list of global constants.  We'll convert them to g later.
#Each global constant is a tuple of:
# (parameterName, distributionFn, distributionFnArgsExceptForLabel, fixedValue, isFixed=0)
gc=[]

########
##  Time bin definitions for the historical information.

#This is the number of seconds between time bins in the past:
gc.append(('pastTimeBinsIncrementSec', hp.uniform, (1*60*60, 30*24*60*60), 60*60*24, 1))

#How many time bins of past information to use, maximum.  If we have less than that, then less will 
# be used:
##NOTE:  This is the only parameter I know of that significantly effects what data is used in 
# the testing step.  It's a source of leak from parameters to the testing result.
# When this varries, some of the data in the testing set for some runs is actually in the 
# training set for other runs.  I think the way to handle this is to do a couple optimizations 
# where this can varry to get the right number range, and then to fix it and make sure that the 
# final optimization run you do has this fixed, so we don't ever let testing data into our 
# training.
gc.append(('pastTimeNumBinsMax', hp.quniform, (1, 10*365, 1), 5*365, 0))

#####
#  Time bin definitions for future information.  This probably should stay fixed since it has 
# more to do with our investing strategy than anything else.

#This is the number of seconds between time bins in the future:
#Putting this in variable mode seems to cause a lot of NaN problems, so I recommend you fix it:
gc.append(('futureTimePointsIncrementSec', hp.uniform, (1*60*60, 30*24*60*60), 60*60*24, 1))

#Our geometric progression factor for the future time points:
gc.append(('futureTimePointsMultiplier', hp.uniform, (1, 10), 2, 1))

#How many time bins of future information to try and predict:
gc.append(('futureTimePointsNum', hp.quniform, (1, 5, 1), 2, 1))

######

#Number of samples per time bin to use:
##TODO: Increase the max once we have a lot of data.
gc.append(('samplesPerTimeBin', hp.quniform, (1, 50, 1), 1, 1))

#What amount of the shaped data in each timestep to enforce to be text and not variable data,
# assuming we have at least one of each we can replicate:
gc.append(('samplesTextRatio', hp.uniform, (.1, .9), .6, 0))

#The number of feature columns we use to encode the user the information is from:
gc.append(('numFeaturesForUser', hp.quniform, (4, 64, 1), 4, 1))

######

#Says if we should make our variable data stationary before training the neural network with it:
gc.append(('variablesMakeStationary', hp.randint, (1,),  0, 0))
            
#What spacy language model we should use:
#Right now we just have one, but we could install several and compare their performance:
gc.append(('spacyLanguageModel', hp.choice, (('en',),), 'en', 1))

#The maximum n-gram to use for our terms.  n-grams up to this are used as well:
gc.append(('textNgramMax', hp.quniform, (1, 2, 1), 2, 0))

#This is the maximum number of terms that can be put into termsThatMatter to help predict 
#each output variable.  Must be >= 2 to work because the actual number is floor(num/2)*2
gc.append(('numTermsPerOutputVarMax', hp.quniform, (2, 256, 1), 4, 0))

##########
# For data reshaping:

#This is how many time bins are in each window:
#TODO: Increase the max once we have a lot of data.
gc.append(('windowSizeTimeBins', hp.quniform, (2, 25, 1), 10, 0))

#This is how many time bins we increment between different windows.  0 would give us the same 
# window over and over again: (integer: 1-30)
gc.append(('windowIncrementTimeBins', hp.quniform, (1, 5, 1), 1, 0))

############

##########
## Building the neural network:
#

#Says if we should use LSTM as a cell or GRU:
gc.append(('useLSTMNotGRU', hp.randint, (1,), 1, 0))


##TODO:  When we have more data, increase this max as well:
#How many meta layers to use (may have multiple layers in it) that are shared by all of the outputs:
gc.append(('numMetaLayersShared', hp.quniform, (1, 5, 1), 3, 0 ))

#How many cells that the first layer should have:
gc.append(('numCellsStart', hp.quniform, (1, 100, 1 ), 5, 0 ))

# How many fewer cells to have in each metaLayer: (.2-1)
gc.append(('cellReductionFactor', hp.uniform, (.2, .9), .5, 0))

gc.append(('rnnActivation', hp.choice, (('tanh', 'relu'),), 'tanh', 0)) 

# Fraction of the units to drop for the linear transformation of the inputs.
gc.append(('rnnDropout', hp.uniform, (0, .3), 0, 0))

# Fraction of the units to drop for the linear transformation of the recurrent state:
gc.append(('rnnRecurrantDroput', hp.uniform, (0, .3), 0, 0))

#Which implementation to of the RNN cell calculations.  This shouldn't affect the answer but 
# should affect the speed dependong on the hardware.  Either 1 or 2.
gc.append(('rnnImplementation', hp.choice, ((1,2),), 1, 0))

#How many samples to use in each training batch:
gc.append(('fitBatchSize', hp.quniform, (1, 2048, 1 ), 2048, 0))

#How many consecutive epochs without any improvement in val_loss we allow before we stop training:
#20-30 seemed like a good value.  We might be missing out on some accuracy, so let's test more.
gc.append(('fitEarlyStoppingPatience', hp.quniform, (20, 500, 1 ), 500, 0))

#The maximum number of epochs to use when training.  We have early-stopping enabled so hopefully
#we won't reach this very often.
gc.append(('fitEpochs', hp.quniform, (1, 500, 1 ), 1, 0))

#Which optimizer to use:
optimizerChoices=('RMSProp', 'SGD', 'Adagrad', 'Adadelta', 'Adam', 'Adamax', 'Nadam' )
gc.append(('optimizer', hp.choice, (optimizerChoices,), optimizerChoices[0], 0))

#######################

#Produce g and searchSpace and other variables we will be importing from other files:
(g, searchVarNamesInOrder, fixedParamDict, searchSpace)=GCExtract(gc)
