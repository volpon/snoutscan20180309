from namedlist import namedlist

##Define our global constants as a named list. (https://pypi.python.org/pypi/namedlist)

## WARNING: Constants are now set at the bottom of this file, not here:
GCNamedList=namedlist('GCNamedList', 
                      [('canonicalSampleRate', 6471),
                       ('featuresNumSamplesInFFTLog2', 8),
                       ('featuresSampleOverlapRatio', 0.25),
                       ('featuresFreqResizeAmount', 0.88),      # How much to shrink the spectrogram freq.
                       ('featuresWindowSize', 5),               # Rob says his humans need 500ms or more for most noises.
                       ('fftFeatFreqRangeMin', 100),            # min freq for FeaturesFFTExtract.
                       ('fftFeatFreqRangeMax', 2000),           # max freq for FeaturesFFTExtract.
                       ('neuralNetNumNeurons', 1),              # The number of neurons in the hidden layer.
                       ('neuralNetActivationFn', 1),            # The activation function (0=logistic, 1=tanh, 2=relu)
                       ('neuralNetOptAlg', 3),                  # The optimization alg. for backprop. {0:'l-bfgs', 1:'sgd', 2:'adam'}
                       ('neuralNetRegularzation', .0001),       # L2 pentalty - a regularization term
                       ('neuralNetInitLearningRatePow', .001),  # The initial learning rate is .1^pow
                       ('neuralNetLearningRateSched', 1),       # The learning rate schedule {0:'constant', 1: 'invscaling'}
                       ('neuralNetTol', .0001),                 # Tolerance of error considered "good enough"
                       ('neuralNetSdgMomentum', .9),            # Momentum constant for sgd algorithm.
                       ('neuralNetSdgNestervosMomentum', 1),    # Whether or not to use nestervos momentum for sgd algorithm.
                       ('neuralNetValidationFraction', .1),     # Proportion of training data to use as validation for early stoping
                       ('neuralNetAdamBeta1', .9),              # Exponential decay rate for estimates of first moment vector in adam
                       ('neuralNetAdamBeta2', .999),            # Exponential decay rate for estimates of second moment vector in adam
                       ('classFreqFairTol', 1.1),               # Tolerance around class frequency equality. 1=completely equal class freq.
                       ('samplesOutInRatio', .2),               # What proportion of the samples to keep when balancing
                       ])
                      
#Define the domain (min and max that makes sense) of each varible:
gcDomain=GCNamedList([5000, 12000],  #canonicalSampleRate
                     [6, 12],        #featuresNumSamplesInFFTLog2 (Corresponds to 64 - 2048)
                     [.1, .9],       #featuresSampleOverlapRatio
                     [.2, 1],        #featuresFreqResizeAmount
                     [1, 20],        #featuresWindowSize (will be rounded to the nearest odd number)
                     [0, 200],       #fftFeatFreqRangeMin
                     [400, 3000],    #fftFeatFreqRangeMax
                     [1, 100],       #neuralNetNumNeurons
                     [0, 2.999],     #neuralNetActivationFn
                     [0, 2.999],     #neuralNetOptAlg
                     [0, .002],      #neuralNetRegularzation
                     [1, 8],         #neuralNetInitLearningRatePow
                     [0, 1.999],     #neuralNetLearningRateSched
                     [1e-5, 1e-1],   #neuralNetTol
                     [.5, .95],      #neuralNetSdgMomentum
                     [0, 1.999],     #neuralNetSdgNestervosMomentum
                     [.05, .5],      #neuralNetValidationFraction
                     [.8, .99],      #neuralNetAdamBeta1
                     [.9, .9999],    #neuralNetAdamBeta2
                     [1, 3],         #classFreqFairTol
                     [.2, 1],        #samplesOutInRatio
                     )

#g stands for "global constants"
##Instantiate the list, with defaults.
g=GCNamedList();

def SetConstants(constantList):
  '''
  This function is used to overwrite the constants from a normal list.
  Used in the Metric Optimization Engine to set parameters for the system.
  '''
  global g  
  #Update our global variable with the data from constantList:
  g=GCNamedList(*constantList);
  
#Update list with our best values so far:
SetConstants([5216.19118995, 9.6154968296, 0.378215193787, 0.616429340287, 4.3198546379, 29.1015969153, 
               1801.65920047, 41.8472053456, 2.36744662227, 1.66366031535, 0.000900124980205, 2.19190591221, 
               0.896389900254, 0.0548655339533, 0.7491208793, 1.11510782413, 0.293042701036, 0.950803541085, 
               0.977055735765, 2.66233820729, 0.899952706712]);