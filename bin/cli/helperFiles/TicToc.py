#Make python 2 and 3 compliant so that ArgsParseOptimize (written in python2 so it can be used with 
# MOE) can use it:
from __future__ import absolute_import, division, print_function
import time
import sys

#This is made a class so that we can have different instantiations of it if we want to write
# threadsafe code.
class TicToc:
  startTimesForTictoc=[];

  #This stores our indent levels for each started Tic()
  indentLevelsForTictoc=[];

  outFile=None

  #Our initializer only takes the file to output to, defaulting to sys.stdout:
  def __init__(self,  verbosityLevel=10000, quietAlways=False, labelEnding='...', outFile=sys.stderr,):
    self.verbosityLevel=verbosityLevel
    self.quietAlways=quietAlways
    self.outFile=outFile
    self.indentLevel=0
    self.labelEnding=labelEnding
    
    #Says if this is the first time we've used Tic()
    self.firstUse=True

  #This starts a timer, indented at our nesting level.
  def Tic(self,label=''):
    '''Used for timing segments of code.  Adds a start time to the timer stack.  Use Toc to finish.'''
    
    #If we have a label and we are verbose enough:
    if label is not '' and self.verbosityLevel>self.indentLevel:
      
      #If we're in one of the first two levels, put 
      if self.indentLevel in (0,1) and not self.firstUse:
        print('', file=self.outFile)
      
      #Indent this many times:
      print ("  "*(self.indentLevel), end='',file=self.outFile)

      #Then, print the label:
      print(label+self.labelEnding, file=self.outFile)
    
    #Append our start time to the stack:
    self.startTimesForTictoc.append(time.time());
    
    #Store our indent level for this time:
    self.indentLevelsForTictoc.append(self.indentLevel)
    
    #Increment our indent level for the next new Tic()
    self.indentLevel+=1
    
    self.firstUse=False
    
  def Toc(self, quietMode=False):
    '''This closes the last started timer and removes it from the stack, printing the elapsed time.'''
  
    #Get our indent level from the stack:
    indentLevel=self.indentLevelsForTictoc.pop()
        
    elapsedTime=(time.time() - self.startTimesForTictoc.pop())

    #If we're verbose enough to display stuff and and not in quiet mode:
    if self.verbosityLevel>self.indentLevel and not (quietMode or self.quietAlways):
      #Indent this many times:
      print ("  "*(indentLevel+1), end='',file=self.outFile)
        
      try: 
        #I limit it to 5 decimal places because just calling tic() and toc() takes around 1-3 e-6.
        print("Elapsed time is %.5f seconds." % elapsedTime,file=self.outFile)
      except:
        print("toc: start time not set",file=self.outFile)
        
      print ('', file=self.outFile)
    
      
    #Decrement our indent level for the next new Tic()
    self.indentLevel+=-1
      
    return elapsedTime
  
  #def p(self,varStr):
    #'''
    #This function prints a variable represented by the string varStr (variable name), in a human readable way, 
    #and at the appropriate indentation level.
    #'''
    
    ##Get the last indentation level:
    #indentLevel=self.indentLevelsForTictoc[-1]
    
    ##Print the variable, with the appropriate indentation amount:
    #print ("  "*(indentLevel+1) + '%s = "%s"' % (varStr, str(eval(varStr))),file=self.outFile)



#So that Tic and Toc can still be used in a functional, global way, make one default, global 
# instance of it, and define Tic and Toc to be in reference to that object.

ticTockGlobalInstance=TicToc()
Tic=ticTockGlobalInstance.Tic
Toc=ticTockGlobalInstance.Toc

class TT():
  '''
  This is a context-manager interface for TicToc.
    
  See __init__() for usage info.
  '''


  def __init__(self, message, quietMode=False, ticTocInstance=ticTockGlobalInstance):
    '''
    Inputs:
      message         - What message to display on Tic():
      quietMode       - If True, don't actually print times for this level.
      ticTocInstance  - A tictoc instance to use.  If none provided, the global ttTicTocInstance is used if
                        it is there.  Otherwise, the the global instance ticTockGlobalInstance is used.
  
    We use TT.ticTocInstance as a way to set what our ticToc instance will be for all TT's made in the future:
  
    Usage:
      with TT('Entering loop'):
        ...
    '''
    
    #Check to see if we already have a ticTocInstance (set outside this class with TT.ticTocInstance):
    if 'ticTocInstance' in dir(TT):
      #Set self.ticTocInstance with that:
      self.ticTocInstance=TT.ticTocInstance
    else:
      #Get it from our init argument:
      self.ticTocInstance=ticTocInstance
      
    self.message=message
    self.quietMode=quietMode
  
  def __enter__(self):
    self.ticTocInstance.Tic(self.message)

  def __exit__(self, *args):
      self.ticTocInstance.Toc(self.quietMode)



