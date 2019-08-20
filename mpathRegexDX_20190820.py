########################################################################
#   Project: Regex classification functions for MPATH DX Groups
#   Author: Nick Kurtansky
#   Date: 8/20/2019
# 
#   Functions utilizing regex to classify a string (path dx) into one of
#   the following Dx groups:
#       lentigo related
#       nevus and related
#       atypia
#       atypical spitzoid lesion
#       melanocytic lesion of uncertain malignant potential
#       mis
#       invasive melanoma
#       non-melanocytic lesion
########################################################################


import statistics
import os
import pandas as ps
import re
import numpy as np
import datetime
import string as stringmod


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


#### NEW PROTOCAL 190722
def no_AND_maybe_pat(string, no_pat, maybe_pat):
    # initialize
    out = [0,0,'']
    
    # test patterns
    if type(maybe_pat.search(string)) == re.Match:
        return([0,1,maybe_pat.search(string).group(0)])

    elif type(no_pat.search(string)) != re.Match:
        return([1,0,''])

    out[2] = no_pat.search(string).group(0)
    # 2 = hard dx
    # 1 = soft dx
    # 0 = negative for the condition
    return(out)


def MPATH_dx(string):
    # initialize
    dx_1 = ['',0,0]
    dx_2 = ['']
    
    # if empty string => no dx possible
    if string == '':
        return(dx_1 + dx_2)
    # rid string of extra whitespaces
    string = re.sub(r'\s{2,}', r' ', string)
    
#    # For when a breslow thickness is given, we need to disregard the exact measurement
#    # so that the algorithm doesn't think the period in 0.2 mm is the end of sentence.
#    string = re.sub(r'.\d\d mm', r'', string)
#    string = re.sub(r'.\d mm', r'', string)

    # Ex) overall does not meet criteria for a more atypical process e.g. melanoma.
    string = re.sub(r'e.g.', r'', string)
    
    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    string_chop = string[string.find(':'): ]   
    string = '  {}  '.format(string)
    string_chop = '  {}  '.format(string_chop)
    strings = [string_chop, string]

    #### NEW PROTOCAL 190801
    # choose one of the 7 MPATH Dx
    for st in strings:
        melanoma = MPATH_mel(st)
        if melanoma[0] == 1:
            if max(melanoma[3:5]) == 1:
                dx_1 = ['Invasive melanoma'] + melanoma[3:5]
                if max(melanoma[1:3]) == 1:
                    dx_2 = ['Melanoma in situ']
                #return(['Invasive melanoma'] + melanoma[3:5])
            else:
                dx_1 = ['Melanoma in situ'] + melanoma[1:3]
                #return(['Melanoma in situ'] + melanoma[1:3])
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)
        
        # but if the word melanoma appears anywhere in the DX, it should at least be dx_2
        if dx_1 == ['',0,0]:
            if any(item.replace(' ', '') in st.replace(' ', '') for item in ['melanoma', 'lentigo maligna']):
                dx_2 = ['Melanoma']
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)
        
        nevus = MPATH_nevus(st)
        # aimp
        if max(nevus[1:3]) != 0:
            if dx_1 == ['',0,0]:
                dx_1 = nevus[0:3]
            elif dx_2 == ['']:
                dx_2 = nevus[0:3]
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)

        # atypical spitzoid lesion
        if max(nevus[4:6]) != 0:
            if dx_1 == ['',0,0]:
                dx_1 = nevus[3:6]
            elif dx_2 == ['']:
                dx_2 = nevus[3:6]
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)
        
        
        # atypical
        if max(nevus[7:9]) != 0:
            if dx_1 == ['',0,0]:
                dx_1 = nevus[6:9]
            elif dx_2 == ['']:
                dx_2 = nevus[6:9]
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)
        
        
        # general nevus
        if max(nevus[10:12]) != 0:
            if dx_1 == ['',0,0]:
                dx_1 = nevus[9:12]
            elif dx_2 == ['']:
                dx_2 = nevus[9:12]
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)
            
            
        lentigo = MPATH_lentigo(st)
        if lentigo[0] != '':
            if dx_1 == ['',0,0]:
                dx_1 = lentigo
            elif dx_2 == ['']:
                dx_2 = lentigo
        # continue until we have a dx_2
        if dx_1 != ['',0,0] and dx_2 != ['']:
            return(dx_1 + dx_2)
            
        elif dx_1 != ['',0,0]:
            return(dx_1 + ['Non-melanocytic lesion'])
        
        else:
            continue        
    return(['Non-melanocytic lesion', 0, 0] + dx_2)


def MPATH_mel(string):
    # Need to check against both invasive AND in-situ melanoma
    # Example: "In-situ melanoma... bla bla bla... No evidence of invasive melanoma"
    # should still be classified as melanoma.  
    invasive = '(?!(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna))(melanoma|invasion)'
    insitu = '(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna)'

    mel = ['melanoma', 'lentigo maligna']
    at_least_insitu = ['invasive', 'invasion', 'breslow', 'depth', 'thick']
    mel_flag_insitu_pat = re.compile("(melanoma[^.;:)]*(in situ|in-situ|insitu)|(in situ|insitu|in-situ)[^.;:)]*melanoma|lentigo maligna)")
    
    invasive_no = no_pattern(invasive)
    invasive_maybe = maybe_pattern(invasive)
    insitu_no = no_pattern(insitu)
    insitu_maybe = maybe_pattern(insitu)
                       
    # Check for any Melanoma flag POSITIVE
    if any(item.replace(' ', '') in string.replace(' ', '') for item in mel):
                    
        # Check for In-Situ flag POSITIVE #################################
        if type(mel_flag_insitu_pat.search(string)) == re.Match:
            
            # if so, create two strings:
            # 1. the original string string
            # 2. the original string minus any instances of 'in situ melanoma'
            st_sub = re.sub(r'(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna)', r'', string)
            st_sub = re.sub(r'\s{2,}', r' ', st_sub)
            st_sub = '  {}  '.format(st_sub)
                        
            # In-Situ dx
            insitu_dx = no_AND_maybe_pat(string, insitu_no, insitu_maybe)              

            # Check if there is still a need to check for invasive dx
            if any(item.replace(' ', '') in st_sub.replace(' ', '') for item in at_least_insitu):

                # Invasive dx
                if breslow_thick(string) != '':
                    invasive_dx = [1,0]
                elif type(re.compile('possible microinvasive').search(st_sub)) == re.Match:
                    invasive_dx = [0,0]
                    #invasive_dx = no_AND_maybe_pat(st_sub, invasive_no, invasive_maybe)
                else:
                    invasive_dx = [1,0]    
            else:
                # Invasive dx
                invasive_dx = [0,0]

        # In-Situe flag NEGATIVE        
        else:
            # In-Situ dx
            insitu_dx = [0,0]

            # Invasive dx
            if breslow_thick(string) != '':
                invasive_dx = [1,0]
            else:
                invasive_dx = no_AND_maybe_pat(string, invasive_no, invasive_maybe)

        # [mel, hard insitu, soft insitu, hard invasive, soft invasive]
        out = [0] + insitu_dx[0:2] + invasive_dx[0:2]
        out[0] = max(out[1:5])
        return(out)
                
    # if all else fails, return no mel
    return([0,0,0,0,0])


def MPATH_lentigo(string):
    #  RESULT FORMAT: [string, #, #] where [MPATH DX = LENTIGO RELATED, HARD DX, SOFT DX]

    # Lentigo related
    lentigo = '(lentigo|ephelis)'       # 190807 edit: combined solar lentigo and lentigo simplex
    if type(re.compile(lentigo).search(string)) != re.Match:
        return(['',0,0])
    no_pat = no_pattern(lentigo)
    maybe_pat = maybe_pattern(lentigo)
    return(['Lentigo related'] + no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2])
    

def MPATH_nevus(string):
    #  RESULT FORMAT: [string, #, #] where [MPATH DX in (NEVUS, ATYPIA, ATYPICAL SPITZ, AIMP), HARD DX, SOFT DX]
    aimpOUT = ['Melanocytic lesion uncertain malignant potential', 0, 0]
    atypspitzOUT = ['Atypical spitzoid lesion', 0, 0]
    atypOUT = ['Atypia', 0, 0]
    nevOUT = ['Nevus and related', 0, 0]

    # LEVEL I
    # nevus and related
    nevusANDrelated = '(nevus|nevi|halo|spitz|spindle cel|lentiginous|melanocytic|melanocytes)'
    # check for lack of any instance of the nevus keywords
    if type(re.compile(nevusANDrelated).search(string)) != re.Match:
        return(aimpOUT + atypspitzOUT + atypOUT + nevOUT)
    no_nevus = no_pattern(nevusANDrelated)
    maybe_nevus = maybe_pattern(nevusANDrelated)
    # if at least nevus, check for extent of atypia

    # LEVEL 3
    aimp = '(aimp|pimp|sumpus|meltump|(atypical|pagetoid)(| intraepithelial| intradermal| intraepidermal) melanocytic (neoplasm|proliferation)|melanocytic tumor[^.]*uncertain(| malignant) potential)'
    if type(re.compile(aimp).search(string)) == re.Match:
        no_pat = no_pattern(aimp)
        maybe_pat = maybe_pattern(aimp)
        # if reasonable evidence for malanocytic lesion of uncertain malignant potential exists
        if max(no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2]) != 0:
            aimpOUT = ['Melanocytic lesion uncertain malignant potential'] + no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2]              
            #(['Melanocytic lesion uncertain malignant potential'] + no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2])

    # LEVEL 2
    # elif, check for moderate atypia
    atypia = '(atypia|atypical|dysplastic|dysplasia|melanocytic proliferation)'    
    if type(re.compile(atypia).search(string)) == re.Match:
        no_pat = no_pattern(atypia)
        maybe_pat = maybe_pattern(atypia)
        # if reasonable evidence for moderate atypia exists, carry on to check for spitz\spindle cell or nevus in general
        if max(no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2]) != 0:
            # spitz?
            spitz = '(spitz|spindle cell)'
            if type(re.compile(spitz).search(string)) == re.Match:
                no_pat = no_pattern(spitz)
                maybe_pat = maybe_pattern(spitz)
                # if reasonable evidence for spitz\spindle cell
                if max(no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2]) != 0:
                    atypspitzOUT = ['Atypical spitzoid lesion'] + no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2]
            # else, Atypia in general
            atypOUT = ['Atypia'] + no_AND_maybe_pat(string, no_pat, maybe_pat)[0:2]

    # else, Nevus and related
    nevOUT = ['Nevus and related'] + no_AND_maybe_pat(string, no_nevus, maybe_nevus)[0:2]

    # return the dx info for all 4 categories
    return(aimpOUT + atypspitzOUT + atypOUT + nevOUT)

    
def no_pattern(keyword_expression):
    no_pat1 = '((\s|-|^\w)((free|absence) of|non-diagnositic|(fail|failed) to reveal|insufficient|negative|no|not)\s[^.;:()]*'
    no_pat2 = '[^.;:()]*(not (seen|identified)|negative))'
    paste = '{}{}|{}{}'.format(no_pat1, keyword_expression, keyword_expression, no_pat2)
    return(re.compile(paste))


def maybe_pattern(keyword_expression):
    maybe_pat1 = "(\s|^\w)(could be|border on|hesitate|possible|not unequivocally|(difficult to|not possible to|cannot|can't|can not)( | entirely )(exclude|rule out)|concerning|suspicious|worrisome|possibility|borderline)[^.]*"
    paste = '{}{}'.format(maybe_pat1, keyword_expression)
    return(re.compile(paste))



