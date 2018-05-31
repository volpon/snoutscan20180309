class Namespace:
    '''
    This class is used to be able to store key:value pairs using a synatax that is more convenient
    than a dictionary.  
    
    If n=Namespace(), then you can use n.<key>=value to set and access values.
    '''
    
    def __init__(self, initialDict={}):
        self.__dict__.update(initialDict)
    
    def AsDict(self):
        '''
        Returns a a dict representation of this namespace object.'
        '''
        return self.__dict__;
