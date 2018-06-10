#Make python 2 and 3 compliant so that ArgsParseOptimize (written in python2 so it can be used with 
# MOE) can use it:
from __future__ import absolute_import, division, print_function
from contextlib import contextmanager
import time
import sys

#This is made a class so that we can have different instantiations of it if we want to write
# threadsafe code.
class TicToc:
  startTimesForTictoc=[];

  #This stores our current indent level:
  indentStack=[];

  outFile=None

  #Our initializer only takes the file to output to, defaulting to sys.stdout:
  def __init__(self,  verbosityLevel=10000, quietAlways=False, labelEnding='...', outFile=sys.stderr,):
    '''
    Inputs:
      verbosityLevel   - How many indentation levels to print.
      quietAlways      - If True, don't actually print times on Toc()'s.
      labelEnding      - What to write at the end of a Tic message.
      outFile          - Where to write things - a file descriptor like object.
    '''
    
    self.verbosityLevel=verbosityLevel
    self.quietAlways=quietAlways
    self.outFile=outFile
    self.labelEnding=labelEnding
    
    #Says if this is the first time we've used Tic()
    self.firstUse=True

  #This starts a timer, indented at our nesting level.
  def Tic(self,label=''):
    '''Used for timing segments of code.  Adds a start time to the timer stack.  Use Toc to finish.'''
    
    #If we have a label and we are verbose enough:
    if label is not '' and self.verbosityLevel>self.indentLevelGet():
      
      #If we're in one of the first two levels, put 
      if self.indentLevelGet() in (0,1) and not self.firstUse:
        print('', file=self.outFile)
      
      #Then, print the label:
      self.print(label+self.labelEnding)
    
    #Append our start time to the stack:
    self.startTimesForTictoc.append(time.time());
    
    self.firstUse=False
    
  def Toc(self, quietMode=False):
    '''This closes the last started timer and removes it from the stack, printing the elapsed time.'''
  

    #If we're verbose enough to display stuff and and not in quiet mode (where we don't display 
    # the toc endings)
    if self.verbosityLevel>self.indentLevelGet() and not (quietMode or self.quietAlways):
      try: 
        #Get our ending time:
        elapsedTime=(time.time() - self.startTimesForTictoc[-1])
        
        #I limit it to 5 decimal places because just calling tic() and toc() takes around 1-3 e-6.
        self.print("Elapsed time is %.5f seconds.\n" % elapsedTime)
      except:
        self.print("toc: start time not set\n")
              
    #Decrement our indent level for the next new Tic():
    self.startTimesForTictoc.pop()
      
    return elapsedTime

  def indentLevelGet(self):
    '''
    This function gets our current indentation level.
    '''
    return len(self.startTimesForTictoc)

  def print(self,s):
    '''
    This function prints a string s at the current indentation level, also indenting new lines
    appropriately.
    '''
        
    #Indent each line with indentLevel*2 spaces:
    s = s.split('\n')
    s = ["  " * (self.indentLevelGet()) + line for line in s]
    s = '\n'.join(s)

    #Print it if we're at this verbosity level at least:    
    if self.verbosityLevel> self.indentLevelGet():
        #Print it:
        print(s, file=self.outFile)
    
  
  def p(self,varStr):
    '''
    This function prints a variable represented by the string varStr (variable name), in a human readable way, 
    and at the appropriate indentation level.
    '''
    
    #Print the variable, with the appropriate indentation amount:
    self.print ('%s = "%s"' % (varStr, str(eval(varStr))))

  @contextmanager
  def TT(self, message, quietMode=False):
    '''
    This is a context manager that calls self.Tic before and self.Toc after.
    '''
    
    #Start it:
    self.Tic(message)
    
    #Run the nested bit of the with clause:
    yield
    
    #Finish it:
    self.Toc(quietMode)
      

#So that Tic and Toc can still be used in a functional, global way, make one default, global 
# instance of it, and define Tic,Toc, and TT to be in reference to that object.

ticTockGlobalInstance=TicToc()
Tic=ticTockGlobalInstance.Tic
Toc=ticTockGlobalInstance.Toc
TT=ticTockGlobalInstance.TT




