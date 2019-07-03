# custom classifier: multilayer perceptron

import util
import random
import math
PRINT = True

class MyClassifier:
  """
  Custom multilayer perceptron classifier
  """
  def __init__( self, legalLabels, max_iterations, layers, perLayer,coef):
    self.legalLabels = legalLabels
    self.type = "custom"
    self.max_iterations = max_iterations
    self.layers=layers
    self.perLayer=perLayer
    self.coef=coef

  def train(self, trainingData, trainingLabels, validationData, validationLabels):
    """
    train and auto tune for best number of iterations
    """
    self.hidden = []
    self.output = {}
    self.features = list(set([ f for datum in trainingData for f in datum.keys() ]));
    for i in range(self.layers):
      self.hidden.append([])
      for j in range(self.perLayer):
        self.hidden[i].append({})
        if i==0:
          for k in self.features:
            self.hidden[i][j][k]=random.random()/10
        else:
          for k in range(self.perLayer):
            self.hidden[i][j][k]=random.random()/10
    for label in self.legalLabels:
      self.output[label]={}
      for i in range(self.perLayer):
        self.output[label][i]=random.random()/10 #assuming layers>0
    bestGuesses=0#find best number of iterations; limit is max_iterations
    bestIterations=0
    bestHidden=[]
    bestOutput={}
    for iteration in range(self.max_iterations):
      self.trainIteration(trainingData,trainingLabels)
      guesses=self.classify(validationData)
      correctGuesses=0
      self.coef=self.coef*0.8 # ?!
      for i in range(len(validationLabels)):
        if guesses[i]==validationLabels[i]:
          correctGuesses+=1
      print "Iteration ",iteration, " correctness ratio:",float(correctGuesses)/len(validationLabels)
      if correctGuesses>bestGuesses:
        bestGuesses=correctGuesses
        bestIterations=iteration
        bestHidden=[]
        bestOutput={}
        for i in range(self.layers):# save the best network so far
          bestHidden.append([])
          for j in range(self.perLayer):
            bestHidden[i].append({})
            if i==0:
              for k in self.features:
                bestHidden[i][j][k]=self.hidden[i][j][k]
            else:
              for k in range(self.perLayer):
                bestHidden[i][j][k]=self.hidden[i][j][k]
        for label in self.legalLabels:
          bestOutput[label]={}
          for i in range(self.perLayer):
            bestOutput[label][i]=self.output[label][i]
    print "Best number of iterations:",bestIterations, " correctness ratio:",float(bestGuesses)/len(validationLabels)
    self.hidden=bestHidden #copy the best network back
    self.output=bestOutput
    
  def trainIteration(self,data,labels):
    #train one iteration
    for datum,label in zip(data,labels):
      res=self.calculateResponses(datum)
      outs=res[self.layers]
      expected={}
      for l in self.legalLabels:
        expected[l]=0
        if l==label:
          expected[l]=1
      self.update(expected,res,datum)
    
  def update(self,expected,res,datum):
    #update output weights
    outerror={}
    hiddenError=util.Counter()
    for label in expected:
      outerror[label]=(expected[label]-res[self.layers][label])*res[self.layers][label]*(1-res[self.layers][label])
      for i in range(self.perLayer):
        hiddenError[i]+=res[self.layers-1][i]*(1-res[self.layers-1][i])*self.output[label][i]*outerror[label]
        self.output[label][i]+=self.coef*res[self.layers-1][i]*outerror[label]
        
    #update middle layers
    for i in range(self.layers-1,0,-1): # from layers-1 to 1, just the middle layers
      oldError=hiddenError
      p=i-1 #previous layer (i is current layer)
      hiddenError=util.Counter()
      for j in range(self.perLayer):
        for k in range(self.perLayer):
          #j is index of next level and k is previous level
          #hidden[i][j][k] is weight between the kth of level i-1 and the jth neuron of level i
          hiddenError[k]+=res[p][k]*(1-res[p][k])*self.hidden[i][j][k]*oldError[j] # I just barely understood it LOL
          self.hidden[i][j][k]+=self.coef*res[p][k]*oldError[j]
    #update first layer
    for i in range(self.perLayer):
      #the errors are still in hiddenError
      for feature in self.features:
        self.hidden[0][i][feature]+=self.coef*datum[feature]*hiddenError[i]
   
  def sigmoid(self,x):
    return 1/(1+math.exp(-x))
  
  def classify(self, testData):
    guesses = []
    for datum in testData:
      res = self.calculateResponses(datum)#now res records activation of all neurons; res[0]through layers-1 are hidden layers, res[layers] is the output layer 
      guesses.append(res[self.layers].argMax())
    return guesses
      
  def calculateResponses(self, datum):
    res = util.Counter()
    res[0]=[]
    for i in range(self.perLayer):
      res[0].append(0)
      for feature in datum:
        res[0][i]+=self.hidden[0][i][feature]*datum[feature]
      res[0][i]=self.sigmoid(res[0][i]) 
    for i in range(self.layers-1):
      l=i+1
      res[l]=[]
      for j in range(self.perLayer):
        res[l].append(0);
        for k in range(self.perLayer):
          res[l][j]+=self.hidden[l][j][k]*res[l-1][k]
        res[l][j]=self.sigmoid(res[l][j])
    res[self.layers]=util.Counter() # just to use argMax
    for label in self.legalLabels:
      res[self.layers][label]=0
      for i in range(self.perLayer):
        res[self.layers][label]+=self.output[label][i]*res[self.layers-1][i]
      res[self.layers][label]=self.sigmoid(res[self.layers][label])
    return res
  
  def findHighInfluenceFeatures(self, label):
    #todo
    odds=util.Counter()
    for feature in self.features:
      odds[feature]=((self.counts[label1][feature][1]+self.k)/self.labelCounts[label1]) / ((self.counts[label1][feature][2]+self.k)/self.labelCounts[label2])
    sorted=odds.sortedKeys()
    n=100
    if n>len(sorted):
       n=len(sorted)
    for i in range(n):
       featuresOdds.append(sorted[i])