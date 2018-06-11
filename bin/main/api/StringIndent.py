 
def StringIndent(s, numSpaces):
    '''
    This function indents a string s by numSpaces.
    '''
    if s is None:
        s=''
    
    s = s.split('\n')
    s = [(numSpaces * ' ') + line for line in s]
    s = '\n'.join(s)
    return s