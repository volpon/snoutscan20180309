import sys
import hashlib
from percache import Cache
from functools import wraps
import time

class CachePersistent(Cache):
    '''
    This is a reusable persistent cache implementation that also can take a list of files into 
    consideration and recalculate when those files changed.
    
    So, for example, if the result of a function depends on that function's code and X's code
    and Y's code, this persistent cache can automatically recaulcate values when those
    functions are changed.  This wrapper also takes into account changes in the function's 
    arguments.
    
    Note:  Read the section on "Caching details" here: https://pypi.python.org/pypi/percache
    about what can and cannot be used in the arguments to cached functions.
    
    This decorator changes the name of the function it wraps.
    
    '''
    
    def __init__(self, backend, fileDependencyList=None, maxAgeSec=60*60*24*7):
        '''
        Note: Since there are decorator arguments, the function is passed to __call__()
        instead. The arguments here are the arguments to the decorator.
        
        Since this inherits the Cache 

        Inputs:
            backend           - If backend is a string, it is interpreted as a filename and a 
                                Python shelve is used as the backend. Shelf creates multiple files
                                using that basename.  Otherwise it is interpreted 
                                as a mapping-like object with a `close()` and a `sync()`  method.
                                This allows to use alternative backends like *shove* or *redis*.
        
            fileDependencyList      - a list of files that the results of the function depend on.

            maxAgeSec               - The number of seconds since last use before something is 
                                      automatically removed from the cache, on initialization.
                                      
        
        #Note:  You can overwrite the __repr function by passing it to the Cache__init__ as well.
                 Right now, we're just using the default.  See the documentation for details.

        ''' 
        
        #print('file dependencies are: ', fileDependencyList, file=sys.stderr)
        
        #Start calculating a hash:
        h= hashlib.md5()
        
        #Create our hash of the file contents:
        for filePath in fileDependencyList:
            with open(filePath, 'rb') as file:
                h.update(file.read())
        
        #Calculate the hash and store it:
        self.__fileDependencyHash = h.hexdigest()            
            
        #Initialize our persistent cache:
        Cache.__init__(self, backend)
        
        #Clean our cache of any old stuff:
        self.clear(maxAgeSec)
        
    def __call__(self, func):
        '''
        Decorator function for caching results of a callable.
        
        Note: 
        This was copied and modified from percache.py, and is 
        Copyright (C) 2010 by Oben Sonne <obensonne@googlemail.com>, with a very permissive
        license to do whatever we want with it, provided a certain notice is included.  Since
        we depend on percache.py, it'll be bundled with any code anway, so I'm considering that
        already satisfied.
        
        '''
        
        def wrapper(*args, **kwargs):
            """Function wrapping the decorated function."""
            
            #This was the line Andy changed to add the dependency hash in:
            ckey = [func.__name__, self.__fileDependencyHash] # parameter hash
            for a in args:
                ckey.append(self._Cache__repr(a))
            for k in sorted(kwargs):
                ckey.append("%s:%s" % (k, self.__repr(kwargs[k])))
            ckey = hashlib.sha1(''.join(ckey).encode("UTF8")).hexdigest()

            if ckey in self._Cache__cache:
                
                result = self._Cache__cache[ckey]
            else:
                result = func(*args, **kwargs)
                self._Cache__cache[ckey] = result
            self._Cache__cache["%s:atime" % ckey] = time.time() # access time
            if self._Cache__livesync:
                self._Cache__cache.sync()
            return result

        return wrapper
    
    
#If called with command line arguments, go into test mode:
if __name__ == '__main__':
    
    from TicToc import TT
    from time import sleep
    from os import path
    
    cacheFile=path.expanduser('~/.cachePersistentTest.cache')
    
    thisFile=path.realpath(__file__)
    
    print('''Testing out CachePersistent.  To demonstrate speedup, do the following:
  1.)  Delete the cache files at:
      %s*
  2.)  Run this again, see how long it takes.
  3.)  Run this a third time and see that it's much faster.
  4.)  Edit the spacing in %s and see that it now takes longer again - dependency altered.
  
  ''' % (cacheFile, thisFile), file=sys.stderr)
    
    
    #Use a cached fibinacci sequence as our test, using this file as our dependency:
    @CachePersistent(cacheFile, [thisFile])
    def fib(n):
        
        with TT('calculating %s(%i)' % (fib.__name__, n)):  
            sleep(.1)
            if n < 2:
                return n
            
            a1=fib(n-2)
            a2=fib(n-1)
            
            return a1+a2
    
    with TT('Calculating fib(7)'):
        fib(7)

        
    
