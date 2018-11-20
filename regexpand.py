import re
import sys

from py_mngr import general as g


def split(string, re_pattern, excl_pattern=None, ignr_pattern=None):
    re_match = _select(string, re_pattern, excl_pattern, ignr_pattern)
    if not re_match: return None
    else:
        items = []
        strt = 0
        for i in range(0,len(re_match)):
            s = string[strt:re_match[i][0]]
            items.append(s)
            strt = re_match[i][1]
        items.append(string[strt:])
        return items


#   _____________________________________________________________________   #


# Returns any matching patterns in a string, not including any that overlap w/ excl_pattern
def match(string, re_pattern, excl_pattern=None, ignr_pattern=None):
    re_match = _select(string, re_pattern, excl_pattern, ignr_pattern)
    if not re_match: return None
    else:
        for i in range(0,len(re_match)):
            r = re_match[i]
            re_match[i] = string[r[0]:r[1]]
        return re_match

# String match / single match
def smatch(string, re_pattern, excl_pattern=None, ignr_pattern=None):
    re_match = _select(string, re_pattern, excl_pattern, ignr_pattern)
    if not re_match: return None
    else:
        for i in range(0,len(re_match)):
            r = re_match[i]
            re_match[i] = string[r[0]:r[1]]
        return re_match[0]

# Removes pattern from string, excluding if pattern overlaps with any excluding pattern
# [ADD] making excl_pattern a list of excl_pattern's
def remove(string, re_pattern, excl_pattern=None, ignr_pattern=None):
    re_match = _select(string, re_pattern, excl_pattern, ignr_pattern)
    if not re_match: return string
    else:
        re_match = g.merge_indices(re_match)
        offset = 0
        for i in range(0,len(re_match)):
            strt = re_match[i][0] - offset
            end = re_match[i][1] - offset
            string = string[:strt]+string[end:]
            offset += (end-strt)
        return string            

# Condition for testing if re_pattern matches the entire string
def verify(string, re_pattern, excl_pattern=None, ignr_pattern=None):
    re_match = _select(string, re_pattern, excl_pattern, ignr_pattern)
    if not re_match: return False
    else:
        re_match = g.merge_indices(re_match)
        if len(re_match) == 1 and (re_match[0][1]-re_match[0][0]) == len(string):
            return True
        else:
            return False

# Replaces all highlighted sections (merged if overlapping) with replace string
def replace(repl_str, string, re_pattern, excl_pattern=None, ignr_pattern=None):
    re_match = _select(string, re_pattern, excl_pattern, ignr_pattern)
    if not re_match: return string
    else:
        re_match = g.merge_indices(re_match)
        return g.replace_indices(string, re_match, repl_str)
            

#   _____________________________________________________________________   #


# Returns a dictionary with respect to defined types and matches to those types
def match_types(string, types):
    type_dict = {}
    for type_name, pattern_list in types.items():
        if not isinstance(pattern_list, list): pattern_list = [pattern_list]
        type_matches = []
        for re_pattern in pattern_list:
            type_matches += re.findall(re_pattern, string)
        for i in range(0,len(type_matches)):
            if isinstance(type_matches[i], tuple):
                type_matches[i] = list(type_matches[i])
        if len(type_matches) == 1: type_dict[type_name] = type_matches[0]
        elif len(type_matches) > 1: type_dict[type_name] = type_matches
    return type_dict


# Splits a string or list of strings into a list of types and strings
# EXAMPLE: 'hello world' >> [{'word':'hello'},' ',{'word':'world'}]
# types = {'exStr':r"['\"](.*)['\"]", 'exRest':r".*"}
def split_types(string, types, remove=False):
    str_list = string
    if isinstance(string, str): str_list = [string]
    for type_name, pattern_list in types.items():
        if not isinstance(pattern_list, list): pattern_list = [pattern_list] 
        for re_pattern in pattern_list:
            select=None; remove=None;
            if isinstance(re_pattern, dict):
                select = re_pattern['select']
                if 'remove' in re_pattern: remove = re_pattern['remove']
            elif isinstance(re_pattern,str): select = re_pattern
            else: raise ValueError('Must pass a regex statement as type\'s key value')
            # Remove all groups in re_pattern
            if remove == None:
                paren_indices = [m.span() for m in re.finditer(r"(?<!\\)[\(\)]", select)]
                looka_indices = [m.span() for m in re.finditer(r"\(\?<?[!=>].*?\)", select)]
                remove = g.replace_indices(select, paren_indices, '', looka_indices)
            i = 0
            while i < len(str_list):
                if not isinstance(str_list[i],str): i+=1; continue
                type_list = re.findall(select, str_list[i])

                for j in range(0,len(type_list)):
                    if isinstance(type_list[j], tuple):
                        type_list[j] = list(type_list[j])
                        k = 0
                        while k < len(type_list[j]):
                            if type_list[j][k] in [None, '']:
                                type_list[j] = type_list[j][:k] + type_list[j][k+1:]
                                continue
                            k += 1
                        if len(type_list[j]) == 1: type_list[j] = type_list[j][0]
                        
                if len(type_list) > 1 and type_list[-1] == '':type_list=type_list[:-1]
                if len(type_list) == 1 and re.findall(remove,str_list[i]) == str_list[i]:
                    str_list[i] = {'type':type_name, 'v':type_list[0]}
                elif len(type_list) >= 1:
                    for j in range(0,len(type_list)):
                        type_list[j] = {'type':type_name, 'v':type_list[j]}

                    new_list = g.zipper(re.split(remove, str_list[i]), type_list)
                    str_list = str_list[:i] + new_list + str_list[i+1:]
                    i += len(new_list)
                i += 1

    if remove == True:
        i = 0
        while i < len(str_list):
            if not isinstance(str_list[i], dict): 
                str_list = str_list[:i] + str_list[i+1:]
            else: i+=1

    return str_list


# Higher level split_types function for applying types inside of a found type
def nested_types(string, types, expand=[]):
    str_list = string
    if not isinstance(str_list, list): str_list = [str_list]
    if not isinstance(expand, list): expand = [expand]
    i = 0
    while i < len(str_list):
        if isinstance(str_list[i], str):
            n_list = split_types(str_list[i], types)
            if not (isinstance(n_list[0], str) and len(n_list)==1):
                if not isinstance(n_list, list): n_list = [n_list]
                str_list = str_list[:i] + n_list + str_list[i+1:]
            else: i += 1
        elif isinstance(str_list[i], dict):
            if str_list[i]['type'] in expand:
                n_list = nested_types(str_list[i]['v'],types,expand)
                if not (isinstance(n_list[0], str) and len(n_list)==1):
                    str_list[i]['v'] = n_list
            i += 1
        else: raise ValueError('Can only pass strings or dictionarys to function')
    return str_list

#   _____________________________________________________________________   #


# Tests all regex patterns across entire string to see entire string meets
# allowed = [" +", "[\"'].*?[\"']"]
def validate(string, allowed):
    str_list = string
    if not isinstance(string, list): str_list = [string]
    if not isinstance(allowed, list): allowed = [allowed]
    for i in range(0,len(str_list)):
        if not isinstance(str_list[i],str): continue
        indices = []
        for j in range(0,len(allowed)):
            indices.extend(m.span() for m in re.finditer(allowed[j], str_list[i]))
        k = 1
        while k < len(indices):
            if indices[0][0] <= indices[k][1] and indices[0][0] >= indices[k][0] \
            or indices[0][0] == indices[k][1]:
                if indices[0][1] > indices[k][1]: indices[0]= (indices[k][0],indices[0][1])
                else: indices[0] = indices[k]
                indices = indices[:k] + indices[k+1:]
                k = 1
            elif indices[0][1] <= indices[k][1] and indices[0][1] >= indices[k][0] \
            or indices[0][1] == indices[k][0]:
                if indices[0][0] < indices[k][0]: indices[0] = (indices[0][0], indices[k][1])
                else: indices[0] = indices[k]
                indices = indices[:k] + indices[k+1:]
                k = 1
            elif indices[0][0] <= indices[k][0] and indices[0][1] >= indices[k][1]:
                indices = indices[:k] + indices[k+1:]
            else: k += 1
        if len(indices) == 1 and indices[0] == (0,len(str_list[i])):
            continue
        else: return False
    return True
            
#   _____________________________________________________________________   #

# Returns the indice ranges of a pattern against a string
def pattern_range(string, re_pattern):
    return [m.span() for m in re.finditer(re_pattern, string)]

def _select(string, re_pattern, excl_pattern, ignr_pattern):
    #if not isinstance(re_pattern, list): re_pattern = [re_pattern]
    #if not isinstance(excl_pattern, list): excl_pattern = [excl_pattern]
    #if not isinstance(ignr_pattern, list): ignr_pattern = [ignr_pattern]
    ignr_match = None
    ignr_str = []
    if ignr_pattern:
        ignr_match = pattern_range(string, ignr_pattern)
        if ignr_match:
            ignr_match = g.merge_indices(ignr_match)
            offset = 0
            for i in range(0,len(ignr_match)):
                ignr_str.append(string[ignr_match[i][0]-offset:ignr_match[i][1]-offset])
                string = string[:ignr_match[i][0]-offset] + string[ignr_match[i][1]-offset:]
                offset += ignr_match[i][1] - ignr_match[i][0]
    re_match = pattern_range(string, re_pattern)
    if excl_pattern:
        excl_match = pattern_range(string, excl_pattern)
        if excl_match:
            re_match = g.indices_overlap(re_match, excl_match, remove=True)
    if ignr_match:
        strt = 0
        for i in range(0,len(ignr_match)):
            string = string[strt:ignr_match[i][0]] + ignr_str[i] + string[ignr_match[i][1]:]
            strt = ignr_match[i][1]
            # Inflate valid re_match_items
            for j in range(0,len(re_match)):
                new_range = [re_match[j][0], re_match[j][1]]
                if re_match[j][0] >= ignr_match[i][0]:
                    new_range[0] += ignr_match[i][1]-ignr_match[i][0]
                if re_match[j][1] > ignr_match[i][0]:
                    new_range[1] += ignr_match[i][1]-ignr_match[i][0]
                new_range = tuple(new_range)
                if re_match[j] != new_range:
                    re_match[j] = new_range
    return re_match

