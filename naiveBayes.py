# naiveBayes.py
# -------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util
import classificationMethod
import math

class NaiveBayesClassifier(classificationMethod.ClassificationMethod):
  """
  See the project description for the specifications of the Naive Bayes classifier.
  
  Note that the variable 'datum' in this code refers to a counter of features
  (not to a raw samples.Datum).
  """
  def __init__(self, legalLabels):
    self.legalLabels = legalLabels
    self.type = "naivebayes"
    self.k = 1 # this is the smoothing parameter, ** use it in your train method **
    self.automaticTuning = False # Look at this flag to decide whether to choose k automatically ** use this in your train method **
    
  def setSmoothing(self, k):
    """
    This is used by the main method to change the smoothing parameter before training.
    Do not modify this method.
    """
    self.k = k

  def train(self, trainingData, trainingLabels, validationData, validationLabels):
    """
    Outside shell to call your method. Do not modify this method.
    """  
      
    # might be useful in your code later...
    # this is a list of all features in the training set.
    self.features = list(set([ f for datum in trainingData for f in datum.keys() ]));
    
    if (self.automaticTuning):
        kgrid = [0.001, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 20, 50]
    else:
        kgrid = [self.k]
        
    self.trainAndTune(trainingData, trainingLabels, validationData, validationLabels, kgrid)
      
  def trainAndTune(self, trainingData, trainingLabels, validationData, validationLabels, kgrid):
    """
    Trains the classifier by collecting counts over the training data, and
    stores the Laplace smoothed estimates so that they can be used to classify.
    Evaluate each value of k in kgrid to choose the smoothing parameter 
    that gives the best accuracy on the held-out validationData.
    
    trainingData and validationData are lists of feature Counters.  The corresponding
    label lists contain the correct label for each datum.
    
    To get the list of all possible features or labels, use self.features and 
    self.legalLabels.
    """

    "*** YOUR CODE HERE ***"
    self.totalCount=len(trainingData)
    self.counts = {}
    self.labelCounts=util.Counter()
    for label in self.legalLabels:
      self.counts[label] = {}
      for feature in self.features:
        self.counts[label][feature]=util.Counter()#for every label and every feature, all possible values should have a count
    for i in range(len(trainingData)):
      self.labelCounts[trainingLabels[i]]+=1
      for feature in trainingData[i]:
        self.counts[trainingLabels[i]][feature][trainingData[i][feature]]+=1
    if self.automaticTuning==False:
      return
    bestGuesses=0#find best k
    bestk=1
    for k in kgrid:
      self.setSmoothing(k)
      guesses=self.classify(validationData)
      correctGuesses=0
      for i in range(len(validationLabels)):
        if guesses[i]==validationLabels[i]:
          correctGuesses+=1
      print "Tried k:",k, " correctness ratio:",float(correctGuesses)/len(validationLabels)
      if correctGuesses>bestGuesses:
        bestGuesses=correctGuesses
        bestk=k
    self.setSmoothing(bestk)
    print "Best k:",bestk, " correctness ratio:",float(bestGuesses)/len(validationLabels)
        
  def classify(self, testData):
    """
    Classify the data based on the posterior distribution over labels.
    
    You shouldn't modify this method.
    """
    guesses = []
    self.posteriors = [] # Log posteriors are stored for later data analysis (autograder).
    for datum in testData:
      posterior = self.calculateLogJointProbabilities(datum)
      guesses.append(posterior.argMax())
      self.posteriors.append(posterior)
    return guesses
      
  def calculateLogJointProbabilities(self, datum):
    """
    Returns the log-joint distribution over legal labels and the datum.
    Each log-probability should be stored in the log-joint counter, e.g.    
    logJoint[3] = <Estimate of log( P(Label = 3, datum) )>
    
    To get the list of all possible features or labels, use self.features and 
    self.legalLabels.
    """
    logJoint = util.Counter()
    
    "*** YOUR CODE HERE ***"
    for label in self.legalLabels:
      logJoint[label]=math.log(self.labelCounts[label])-math.log(self.totalCount)
      for feature in datum:
        logJoint[label]+=math.log(self.counts[label][feature][datum[feature]]+self.k)-math.log(self.labelCounts[label])
    return logJoint
  
  def findHighOddsFeatures(self, label1, label2):
    """
    Returns the 100 best features for the odds ratio:
            P(feature=1 | label1)/P(feature=1 | label2) 
    
    Note: you may find 'self.features' a useful way to loop through all possible features
    """
    featuresOdds = []
       
    "*** YOUR CODE HERE ***"
    odds=util.Counter()
    for feature in self.features:
      odds[feature]=((self.counts[label1][feature][1]+self.k)/self.labelCounts[label1]) / ((self.counts[label1][feature][2]+self.k)/self.labelCounts[label2])
    sorted=odds.sortedKeys()
    n=100
    if n>len(sorted):
       n=len(sorted)
    for i in range(n):
       featuresOdds.append(sorted[i])

    return featuresOdds
    

    
      
