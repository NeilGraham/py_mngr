
#  __ STANDARD FUNCTIONS _________________________________________________  #


# Given a single string and pattern, returns the patterns number of occurrences
def occurs(pattern, string, overlapping=False):
    o = occurs_indices(pattern, string, overlapping)
    if o == None: return 0
    else: return len(o)


# Returns part of string before a pattern and occurrence of that pattern
def after(pattern, string, occurrence=0, overlapping=False):
    o = occurs_indices(pattern, string, overlapping)
    if o == None: return None
    if occurrence >= 0 and occurrence < len(o) \
    or occurrence < 0 and abs(occurrence) <= len(o):
        return string[o[occurrence]+len(pattern):]
    else:
        raise ValueError(pattern+' only occurred '+str(len(o))+' times '+\
        '(Called '+str(occurrence)+')')


# Returns part of string after a pattern and occurrence of that pattern
def before(pattern, string, occurrence=0, overlapping=False):
    o = occurs_indices(pattern, string, overlapping)
    if o == None: return None
    elif occurrence >= 0 and occurrence < len(o) \
    or occurrence < 0 and abs(occurrence) <= len(o):
        return string[:o[occurrence]]
    else:
        raise ValueError(pattern+' only occurred '+str(len(o))+' times '+\
        '(Called '+str(occurrence)+')')


# Given two arrays, creates single array that switches array for every value (removes empty strings)
def zipper(arrA, arrB):
    new_arr = []
    if isinstance(arrA,str) and isinstance(arrB,str):
        new_arr = ''
    i = 0 #Iterator
    while i < len(arrA) and i < len(arrB):
        for arr in [arrA, arrB]:
            if isinstance(arr[i],str):
                if len(arr[i]) > 0: 
                    if isinstance(new_arr, str): new_arr += arr[i]
                    else: new_arr.append(arr[i])
            else: new_arr.append(arr[i])
        i += 1
    for arr in [arrA, arrB]:
        arr = arr[i:]
        j = 0
        while j < len(arr):
            if arr[j] == '': arr = arr[:j] + arr[j+1:]
            else: j += 1
        if arr: new_arr += arr; break
    return new_arr


# Returns an array of indices in which a pattern occurs in a string
def occurs_indices(pattern, string, overlapping=False):
    i = 0 # Iterator
    w = 0 # Wait Amount
    o = [] # Occurrences
    while i + len(pattern) <= len(string):
        if w: w -= 1
        elif string[i:i+len(pattern)] == pattern:
            o.append(i)
            if not overlapping: w += len(pattern)
        i += 1
    if len(o) == 0: return None
    else: return o 


# Returns a list of all methods for an object
# TODO: verbose=True makes it so __method__ functions are returned
def list_methods(obj, verbose=False):
    return [method_name for method_name in dir(obj) if callable(getattr(obj, method_name))]


#  __ INDEX FUNCTIONS _______________________________________________________ 
# |                                                                          |
# |  All 'index parameters' must either be a range (2 length tuple w/ the    |
# |  first item being <= the second item) or an index (single integer).      |
# |__________________________________________________________________________|


# Given a string and list of ranges and indices, replaces with corresponding list of replacements
# If more indice items than replace items, will apply last replace item to all subsequent indice items
# If any indice overlaps any of the indices in exceptions, that indice will be removed from the list
def replace_indices(string, indices, replacements, exceptions=[]):
    if not isinstance(indices, list): indices = [indices]
    if not isinstance(replacements, list): replacements = [replacements]
    if not isinstance(exceptions, list): exceptions = [exceptions]
    
    if len(exceptions) > 0:
        indices = indices_overlap(indices, exceptions, remove=True) 
    
    offset = 0
    i = 0
    while i < len(indices):

        replace = ''

        if i >= len(replacements): replace = replacements[-1]
        else: replace = replacements[i]

        strt = 0; end = 0
        if isinstance(indices[i], tuple):
            strt = indices[i][0] + offset
            end = indices[i][1] + offset
        elif isinstance(indices[i], int):
            strt = indices[i] + offset
            end = strt + 1
        else: raise ValueError('Can only pass a list of tuples or integers as indices')
        
        if end < strt: raise ValueError('Range end is before start '+str(indices[i]))
        offset += len(replace) - (end-strt)

        string = string[:strt] + replace + string[end:]

        i += 1
    return string


# Given a list of indices, merges and overlapping/touching indices
def merge_indices(indices):
    if not isinstance(indices, list): indices = [indices]
    i = 0
    while i < len(indices):
        rs = 0; re = 0;
        if isinstance(indices[i], int):
            rs = indices[i]; re = rs + 1
        elif isinstance(indices[i], tuple):
            rs, re = indices[i]

        j = i+1
        while j < len(indices):
            es = 0; ee = 0;
            if isinstance(indices[j], int):
                es = indices[j]; ee = es + 1
            elif isinstance(indices[j], tuple):
                es, ee = indices[j]

            if rs >= es and rs <= ee \
            or re >= es and re <= ee \
            or rs <= es and re >= ee:
                os = 0; oe = 0
                if rs < es: os = rs
                else: os = es
                if re > ee: oe = re
                else: oe = ee
                
                rs, re = os, oe
                indices = indices[:i]+[(os,oe)]+indices[i+1:j]+indices[j+1:]
            else: j += 1
        i += 1
    return indices


# If any of ref_indices overlap with any of exc_indices, returns list of overlapping indices
# When remove == True, returns list of the indices that were not overlapping
def indices_overlap(ref_indices, exc_indices=[], remove=False):
    if not isinstance(ref_indices, list): ref_indices = [ref_indices]
    if not isinstance(exc_indices, list): exc_indices = [exc_indices]

    if len(exc_indices) == 0: 
        exc_indices = ref_indices

    return_indices = []
    for i in range(0,len(ref_indices)):
        rs = 0; re = 0;
        if isinstance(ref_indices[i], int):
            rs = ref_indices[i]; re = rs + 1
        elif isinstance(ref_indices[i], tuple):
            rs, re = ref_indices[i]

        for j in range(0,len(exc_indices)):
            es = 0; ee = 0;
            if isinstance(exc_indices[j], int):
                es = exc_indices[j]; ee = es + 1
            elif isinstance(exc_indices[j], tuple):
                es, ee = exc_indices[j]
            
            if rs >= es and rs < ee or re > es and re < ee \
            or rs < es and re > ee:
                return_indices.append(i)

    return_list = []
    if remove == True:
        for i in range(0,len(ref_indices)):
            if i not in return_indices:
                return_list.append(ref_indices[i])
    else:
        for i in range(0,len(return_indices)):
            return_list.append(ref_indices[return_indices[i]])
    return return_list

