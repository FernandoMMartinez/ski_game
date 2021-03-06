#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""A simple client to create a CLA model for the ski game."""

import sys
import random
import logging

from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.data.inference_shifter import InferenceShifter

import model_paramsNL


yards = 0
totalsize = 80
slopewidth = 21 #31
slopewidthmin = 23
slopewidthmax = 35
variablewidth = False

# uncomment for repeatable testing data
random.seed()

# number of records to train on
_NUM_RECORDS = 2000 #15000


#-----------------------------------------------------------------------------
# skier functions
#-----------------------------------------------------------------------------
def generate_random(choicelist):
    random_choice = random.choice(choicelist)
    return random_choice

def calc_skier_position(skierposition,predicted):
    if predicted > skierposition:
        skierposition = skierposition + 1
    if predicted < skierposition:
        skierposition = skierposition - 1
    return skierposition

def print_slopeline(paddingleft,tree,skier,slopewidth,skierposition,totalsize,yards,printbool):
    """
    This function prints a line of the slope to the screen (stdout).
    The line includes two trees, and a skier.  Occasionally the
    trees are not printed due to a jump.  The width of the slope is
    static for now, and the random number is used to determine how
    far from the left side of the screen the slope begins.
    0--------------t--------S----------t-------------
    """
    treeleft = paddingleft + 1
    leftspace = skierposition - treeleft - 1
    rightspace = slopewidth - leftspace - 1
    treeright = treeleft + slopewidth + 1
    paddingright = totalsize - treeright
    if printbool:
        print paddingleft*"." + tree + leftspace*"." + skier + rightspace*"." + tree + paddingright*".", yards

    return {'treeleft': treeleft, 'pos': skierposition, 'treeright': treeright}

def print_slopeline_perfect(padding,tree,skier,slopewidth,totalsize,yards,printbool):
    skierposition = padding + 1 + int(round(float(slopewidth)/2))
    paddingleft = padding
    paddingright = totalsize-(paddingleft+1+slopewidth+1)
    if(paddingright > paddingleft) and (slopewidth%2 == 0):
        skierposition = skierposition+1

    return print_slopeline(padding,tree,skier,slopewidth,skierposition,totalsize,yards,printbool)

def print_slopeline_crash(paddingleft,treeloc,slopewidth,totalsize,yards):
    """
    This function prints a line of the slope to the screen (stdout)
    that indicates the skier crashed.
    """
    tree = "|"
    crashedtree = "*"
    treeleft = paddingleft + 1
    treeright = treeleft + slopewidth + 1
    paddingright = totalsize - treeright
    
    if treeloc == 1:
        print paddingleft*"." + crashedtree + slopewidth*"." + tree + paddingright*".", yards 
    elif treeloc == 2:
	print paddingleft*"." + tree + slopewidth*"." + crashedtree + paddingright*".", yards


def print_stats(records, yards):
    """
    This function prints the final stats after a skier has crashed.
    """
    print "Training patterns: ", records, ", Test Run: ", yards
    return 0


#-----------------------------------------------------------------------------
# nupic functions
#-----------------------------------------------------------------------------
def createModel():
  return ModelFactory.create(model_paramsNL.MODEL_PARAMS)

def runSecondGame():
  global yards #0
  global totalsize #80
  global slopewidth #21
  global widthmin #23
  global widthmax #35
  global variablewidth #boolean, false
  tree = "|"
  skier = "H"
  minpadding = 0
  maxpadding = totalsize-(slopewidth+2)+1
  choicelist_drift = [-2, -1, 0, 1, 2]
  choicelist_width = [-2, 0, 2]

  #create NuPIC model
  model = createModel()
  model.enableInference({'predictionSteps': [1], 'predictedField': 'pos', 'numRecords': 4000})
  inf_shift = InferenceShifter();
 
  #do training here
  print
  print "================================= Start Training ================================="
  print
  yards = 0
  if(variablewidth):
      print "do variable training"
  else:
      for i in xrange(100): #total training sets
          for j in xrange(maxpadding): #one training set
              yards = yards + 1
              record = print_slopeline_perfect(j, tree, skier, slopewidth, totalsize, yards, 1)
              result = inf_shift.shift(model.run(record))

  #check model outputs
  model.disableLearning()
  print
  print "=============================== Validation ========================================"
  print
  yards = 0
  for i in xrange(maxpadding):
     record = print_slopeline(i,tree, skier, slopewidth, i+2, totalsize, yards, 0)
     result = inf_shift.shift(model.run(record))
     inferred = result.inferences['multiStepPredictions'][1]
     predicted = sorted(inferred.items(), key=lambda x: x[1])[-1][0]
     print_slopeline(i, tree, skier, slopewidth, int(round(predicted)), totalsize, yards, 1) 

  
  #asdfsdf
  #do actual run here
  model.disableLearning()
  print
  print "=================================== Begin Game ==================================="
  print
  random.seed() #set this again or it will use the NuPIC seed
  yards = 0
  change = 0
  padding = random.randint(minpadding, maxpadding)
  skierposition = (padding + (slopewidth)/2)
  while True:
    yards = yards + 1
    if (variablewidth):
        change = generate_random(choicelist_width)
        slopewidth = slopewidth + change
        if slopewidth > slopewidthmax:
            slopewidth = slopewidthmax
        if slopewidth < slopewidthmin:
            slopewidth = slopewidthmin

    drift = generate_random(choicelist_drift)
    padding = padding + drift
    if padding > maxpadding:
        padding = maxpadding
    if padding < minpadding:
        padding = minpadding

	padding = padding - (change/2)
    if padding < 0:
        padding = 0
    if (padding + slopewidth + 2) > totalsize:
        padding = totalsize - (slopewidth+2)

    if ((skierposition - (padding+1)) < 1):
        print_slopeline_crash(padding,1,slopewidth,totalsize,yards)
        break
    if (skierposition - (padding+1) > slopewidth):
        print_slopeline_crash(padding,2,slopewidth,totalsize,yards)
        break
    
    #pring ski text, get current ski data for NuPIC model
    record = print_slopeline(padding,tree,skier,slopewidth,skierposition,totalsize,yards,1)

    #do NuPIC model ski position calculation
    result = inf_shift.shift(model.run(record))
    inferred = result.inferences['multiStepPredictions'][1]
    predicted = sorted(inferred.items(), key=lambda x: x[1])[-1][0]
    skierposition = calc_skier_position(skierposition, predicted)
    


if __name__ == "__main__":
  #test = print_slopeline(5, '|', 'H', 10, 13, 25, 0, 1)
  #print test
  #test2 = print_slopeline_perfect(4, '|', 'H', 10, 25, 0, 1)
  #print test2
  #print_slopeline_crash(4,1,10,25,10)
  #print_stats(100, 10)
  #print int(round(random.uniform(0,60)))
  #print 
  #print 
  

  runSecondGame()

  asdf

  model = createModel()
  model.enableInference({'predictionSteps': [1], 'predictedField': 'pos', 'numRecords': 4000})
  inf_shift = InferenceShifter();

  
  for i in xrange(10):
     for j in xrange(14):
        record = print_slopeline_perfect(j, '|', 'H', 10, 25, 0, 1)
        result = inf_shift.shift(model.run(record))

  print
  print

  model.disableLearning()
  for i in xrange(14):
     record = print_slopeline(i,'|', 'H', 10, i+2, 25, i, 0)
     result = inf_shift.shift(model.run(record))
     inferred = result.inferences['multiStepPredictions'][1]
     predicted = sorted(inferred.items(), key=lambda x: x[1])[-1][0]
     print_slopeline(i, '|', 'H', 10, int(round(predicted)), 25, i, 1) 


  #record = print_slopeline(3,'|', 'H',10, 13, 25, 0, 1)
  #result = inf_shift.shift(model.run(record))
  #inferred = result.inferences['multiStepPredictions'][1]
  #predicted = sorted(inferred.items(), key=lambda x: x[1])[-1][0]
  #print predicted
  #print_slopeline(3, '|', 'H', 10, int(round(predicted)), 25, 0, 1)
  #skierposition = calc_skier_position(13, predicted)
  #print skierposition

  #runGame()
  #print_stats()
  #for n in xrange(1):
      #_NUM_RECORDS = (n+1)*2000+1000
      #runGame()
      #print_stats()
      

