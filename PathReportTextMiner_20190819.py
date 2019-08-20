########################################################################
#
#   Project: Melanoma Dx Path Report Scraper - Presentation
#   Author: Nick Kurtansky
#   Date: 7/24/2019
#
#   Per Lesion Table
#   From Pathology Reports   
#   Let algorithm classify each lesion and track the ways phrases are used.
#       I intend to create frequency distributions out of this data.
#   Count the length of each path_i dx.
#       I intend to check if this is statistically significant with
#       misclassifications and/or the strength/conviction in the path dx.
#  
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


def clinical_dx_section(string):
    # pinpoint start of clinical dx section
    s_start = string.find('clinical diagnosis')
    string = string[s_start: ]
    string = string.replace('clinical diagnosis & history:', '')
    string = string.replace('clinical diagnosis and history:', '')
    string = string.strip()

    # pinpoint end of clinical dx section
    EndIndex = [len(string)]    
    # add to this list of words signalling end of secion
    clinDxEnds = ['specimens submitted', 'cytologic diagnosis', 'lmp:'] 
    for e in clinDxEnds:    
        EndIndex.append(string.find(e))
    EndIndex = [e for e in EndIndex if e != -1]
    EndIndex = min(EndIndex)
    
    return(string[ :EndIndex].strip())

    
def path_dx_section(string):
    # pinpoint start of DIAGNOSIS:
    clin_start = string.find('clinical diagnosis')      # don't mistakenly recognize clin dx
    if clin_start != -1:
        string = string[clin_start: ]       # in case there is no CLININCAL DX secion
    path_start = string.find('diagnosis:')
    if path_start == -1:                   # in case there is no 'DIAGNOSIS: ' section  
        return('')
    string = string[path_start: ]
    string = string.replace('diagnosis:', '')
        
    # pintpoint end of DIAGNOSIS:
    EndIndex = []
    # add to this list of words signalling end of secion
    pathDxEnds = ['specimen source', 'i attest that the above', 'diagnostic interpretation:', 'report electronically signed out', 'gross description:']
    for p in pathDxEnds:
        EndIndex.append(string.find(p))
    EndIndex = [e for e in EndIndex if e != -1]
    if EndIndex == []:
        string = string[ : ]
    else:
        EndIndex = min(EndIndex)
        
        return(string[ :EndIndex].strip())


def lesion_r_path(string):
    if string == None:
        return('')
    lis = string.split('\r\n')
    if len(lis) == 1:
        lis = string.split('\n')
    index_lis = []
    for i in range(len(lis)):
        item = lis[i]
        item = item.strip()
        index_lis.append(i)
    lis = ' '.join(lis[x] for x in index_lis)
    lis = re.sub(r'\s{2,}', r' ', lis)
    return(lis)


def spec_submit_section(string):
    # pinpoint start of SPECIMENS SUBMITTED:
    start = string.find('specimens submitted:')
    # return null value if no such section
    if start == -1:
        return('')
    string = string[start: ]
    
    # pinpoint end of SPECIMENS SUBMITTED:
    end = string.find('diagnosis:')
    if end != -1:
        return(string[ :end])
    else:
        return(string)
        

def lesion_i_clin(index, string):
    # clean up string
    string = string.replace('\r\n', ' ').replace('\n', ' ')
    lis = re.split('site ', string)
    if len(lis) == 1:
        lis = string.split(' ')
        
    # pinpoint components of lis regarding index i
    index = str(index)
    index_lis = []
    for i in range(len(lis)):
        item = lis[i]
        item = item.strip()
        if item == '':
            continue
        if item[0] == index:
            index_lis.append(i)
            
            # continue until yo ucome across a different index
            j = i + 1
            while(j <= len(lis) - 1) and (is_number(lis[j]) == False):
                index_lis.append(j)
                j += 1
    
    # return as one string
    lis = ' '.join(lis[x] for x in index_lis)
    
    return(lis)
        

def lesion_i_path(index, string):
    # clean up string and split at start of new lines
    #string = string.replace(' ', '')
    if string == None:
        return('')
    lis = string.split('\r\n')
    if len(lis) == 1:
        lis = string.split('\n')
        
    # regex to check for time
    ampm = re.compile('\d(:\d\d|:\d\d|)(am|pm)')
    
    # regex to check for breslow thickness
    breslow = re.compile('(\d.\d{0,2}|.\d{0,2}|\d)( |)mm')
    
    # regex to check for mitotic index
    mitotic = re.compile('\d/mm2')
    
    index = str(index)
    
    # pinpoint components of lis regarding index i
    index_lis = []
    for i in range(len(lis)):
        item = lis[i]
        item = item.strip()
        #string = re.sub(r'\s{2,}', r' ', string)
        if item == '':
            continue
        index_len = len(str(index))
        if item[0:int(index_len)] == index:
            index_lis.append(i)
            
            # continue until you come across a different index
            j = i + 1
            while ((j <= len(lis)-1) and (((lis[j].strip() == '') or (is_number(lis[j].strip()[0]) == False)) or ((type(ampm.match(lis[j].strip())) == re.Match) or (type(mitotic.match(lis[j].strip())) == re.Match) or (type(breslow.match(lis[j].strip())) == re.Match)))):         
                index_lis.append(j)
                j += 1
    
    # return as one string
    lis = ' '.join(lis[x] for x in index_lis)
    lis = re.sub(r'\s{2,}', r' ', lis)
    return(lis)


def days_since_collecting_report(string):
    # date format mm/dd/yyyy
    date_pat = re.compile('\d{1,2}/\d{1,2}/\d{4}')
    format_str = '%m/%d/%Y'
    
    # clean up string
    string = string.lower()
    
    # locate Date of Collection/Procedure/Outside Report:
    string_a = string[string.find('date of collection/procedure/outside report:'): ]
    date_a = datetime.datetime.strptime(date_pat.search(string_a).group(0), format_str)
    
    # locate Date of Report:
    string_b = string_a[string_a.find('date of report:'): ]
    date_b = datetime.datetime.strptime(date_pat.search(string_b).group(0), format_str)
    
    # return time between a and b
    return((date_b - date_a).days)
    
    

def number_les_in_report(string):
    # initialize # in report
    lesions_no = 1
    index_len = len(str(lesions_no))

    # pinpoint start of DIAGNOSIS:
    start = string.find('clinical diagnosis')    # don't mistakenly recognize clin dx
    string = string[start: ]
    start = string.find('diagnosis:')
    if start == -1:                     # in case there is no 'DIAGNOSIS: ' section  
        string = string[ : ]
    else:
        string = string[start: ]
    
    # pintpoint end of DIAGNOSIS:
    EndIndex = []
    pathDxEnds = ['specimen source', 'i attest that the above', 'diagnostic interpretation:', 'report electronically signed out', 'gross description:']

    for p in pathDxEnds:
        EndIndex.append(string.find(p))
    EndIndex = [e for e in EndIndex if e != -1]
    if EndIndex == []:
        string = string[ : ]
    else:
        EndIndex = min(EndIndex)
        string = string[ :EndIndex]
    
    # find the number of lesions reported in DIAGNOSIS:
    string = string.replace(' ', '')
    lis = string.split('\r\n')
    
    # regex to check for time
    ampm = re.compile('\d(:\d\d|:\d\d|)(am|pm)')
    
    # regex to check for breslow thickness
    breslow = re.compile('(\d.\d{0,2}|.\d{0,2}|\d)( |)mm')
    
    # regex to check for mitotic index
    mitotic = re.compile('\d/mm2')
    
    # regex to check for start of LESION DIAGNOSIS character
    i2 = re.compile('\d{1,2}(\w|)[|.|:|;|\)]')
    
    if len(lis) == 1:
        lis = string.split('\n')
    for c in lis:
        c = c.strip()
        if c == '':
            continue
        if is_number(c[0:index_len]) == True:
            #if len(c) > 1:
                #if is_number(c[1]) != True:
            if (int(c[0:index_len]) > lesions_no) and (int(c[0:index_len]) - lesions_no == 1) and (type(ampm.match(c)) != re.Match) and (type(mitotic.match(c)) != re.Match) and (type(breslow.match(c)) != re.Match) and (type(i2.match(c)) == re.Match):
                lesions_no = int(c[0:index_len])
        index_len = len(str(lesions_no + 1))
    return(lesions_no)



def vectra_n(string):
    # for the REGEX .+ at beginning and end
    string = ' {} '.format(string)
    
    # REGEX to determine if this info is present
    pat = re.compile('.+[photo #: , vectra #: ].+')
    if type(pat.match(string)) == re.Match:
        # starting location of vectra number in the string
        location = []
        location.append(string.find('photo #:'))
        location.append(string.find('vectra #:'))
        location = max(location)
        string = string[location: ]
        string = string.replace('photo #:', '').replace('vectra #:', '')
        string = string.strip()
        string = '{} '.format(string)
        
        # ending location of vectra number in string
        i = 0
        while is_number(string[i]):
            i += 1
        return(string[0:i])
        
    else:
        return('')


def les_site_i(index, string):
    #index = str(index)
    lis = string.split('\r\n')
    if len(lis) == 1:
        lis = string.split('\n')
    #for item in lis:
    for i in range(len(lis)):
        item = lis[i].strip()    
        if item[0:2] == '{}:'.format(str(index)):
            #if is_number(lis[i+1][0]) == False:
            if lis[i+1].strip()[0:2] != '{}:'.format(str(index + 1)): 
                item = '{} {}'.format(item, lis[i+1]) 
            return(item.strip())
    return(string.replace('specimens submitted:', '').replace('\r\n', ' ').strip())


def dx_nevusarisen(string):
    # if empty string => no path dx
    if string == '':
        return(['', 'N/A'])
    # rid string of extra whitespaces
    string = re.sub(r'\s{2,}', r' ', string)
    
    # For when a breslow thickness is given, we need to disregard the exact measurement
    # so that the algorithm doesn't think the period in 0.2 mm is the end of sentence.
    string = re.sub(r'.\d\d mm', r'', string)
    string = re.sub(r'.\d mm', r'', string)

    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    string_chop = string[string.find(':'): ]
       
    # flag when report specifies '[melanoma] bla bla [arising from] bla bla [nevus]'
    pattern = re.compile('((melanoma|lentigo maligna)[^.]*(arisen|arised|arising|associated|association|evolved|evolving)( in| with| from)[^.]*(nevus)|associated nevus: identified)')
    
    string = '  {}  '.format(string)
    string_chop = '  {}  '.format(string_chop)
    strings = [string_chop, string]
    
    for st in strings:
        # Dx and REGEX checks
        if type(pattern.search(st)) == re.Match:
            foundpattern = pattern.search(st).group(0)
            return(['1', foundpattern])
    # else
    return(['0','N/A'])


def dx_melmets(string):
    # if empty string => no path dx
    if string == '':
        return(['', 'N/A'])
    # rid string of extra whitespaces
    string = re.sub(r'\s{2,}', r' ', string)
    
    # For when a breslow thickness is given, we need to disregard the exact measurement
    # so that the algorithm doesn't think the period in 0.2 mm is the end of sentence.
    string = re.sub(r'.\d\d mm', r'', string)
    string = re.sub(r'.\d mm', r'', string)

    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    string_chop = string[string.find(':'): ]
       
    # flag when report specifies '[melanoma] bla bla [arising from] bla bla [nevus]'
    pattern = re.compile('(metastases|metastasis|metastatic)')
    no_pattern = re.compile('clinical correlation is needed')
    
    string = '  {}  '.format(string)
    string_chop = '  {}  '.format(string_chop)
    strings = [string_chop, string]
    
    for st in strings:
        # Dx and REGEX checks
        if type(pattern.search(st)) == re.Match:
            foundpattern = pattern.search(st).group(0)
            if type(no_pattern.search(st)) != re.Match:
                return(['1', foundpattern])
    # else
    return(['0','N/A'])


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


def melanoma_DX(string, pat_1, pat_2, pat_3, pat_4, pat_5, pat_6, pat_7, pat_8, pat_9, pat_10, pat_11, pat_12, pat_13, pat_14, pat_15, pat_16, pat_17, pat_18, pat_19, pat_20, pat_21, pat_22, pat_23, pat_24, pat_25, pat_26, pat_27, pat_28, pat_29, pat_30, pat_31, pat_32, pat_33, pat_34, pat_35, pat_36, pat_37, pat_38, pat_39, pat_40, pat_41, pat_42):

    # INITIALIZE ALL THE WAYS I SUSPECT THEY MIGHT CLASSIFY A DIAGNOSIS
    explanation = [0 for i in range(42)]
    invasion_list = [0 for i in range(5)]
    location = ''

    # if empty string => no in-situ
    if string == '':
        return([0,0,0,0,0,'','', location] + explanation + invasion_list)
    # rid string of extra whitespaces
    string = re.sub(r'\s{2,}', r' ', string)
    
    # For when a breslow thickness is given, we need to disregard the exact measurement
    # so that the algorithm doesn't think the period in 0.2 mm is the end of sentence.
    string = re.sub(r'.\d\d mm', r'', string)
    string = re.sub(r'.\d mm', r'', string)

    # Ex) overall does not meet criteria for a more atypical process e.g. melanoma.
    string = re.sub(r'e.g.', r'', string)
    
    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    string_chop = string[string.find(':'): ]
   
    # Need to check against both invasive AND in-situ melanoma
    # Example: "In-situ melanoma... bla bla bla... No evidence of invasive melanoma"
    # should still be classified as melanoma.
        
    mel = ['melanoma', 'lentigo maligna']
    mel_pat = re.compile('(melanoma|lentigo maligna)')
    mel_flag_insitu_pat = re.compile("(melanoma[^.;:)]*(in situ|in-situ|insitu)|(in situ|insitu|in-situ)[^.;:)]*melanoma|lentigo maligna)")
    
    mel_no_insitu_pat = re.compile('((\s|-|^\w)((free|absence) of|non-diagnositic|(fail|failed) to reveal|insufficient|negative|no|not)\s[^.;:()]*(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna)|(melanoma|lentigo maligna)[^.;:()]*(not (seen|identified)|negative))')
    mel_no_invasive_pat = re.compile('((\s|-|^\w)((free|absence) of|non-diagnositic|(fail|failed) to reveal|insufficient|negative|no|not)\s[^.;:()]*(?!(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna))(melanoma)|(?!(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna))(melanoma)[^.;:()]*(not (seen|identified)|negative))')

    mel_maybe_insitu_pat = re.compile("(\s|^\w)(could be|border on|hesitate|possible|not unequivocally|(difficult to|not possible to|cannot|can't|can not)( | entirely )(exclude|rule out)|concerning|suspicious|worrisome|possibility|borderline)[^.]*(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna)")    
    mel_maybe_invasive_pat = re.compile("(\s|^\w)(could be|border on|hesitate|possible|not unequivocally|(difficult to|not possible to|cannot|can't|can not)( | entirely )(exclude|rule out)|concerning|suspicious|worrisome|possibility|borderline)[^.]*(?!(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna))(melanoma|invasion)")    
        
    at_least_insitu = ['invasive', 'invasion', 'breslow', 'depth', 'thick']
    invasive_pat = re.compile('invasive')
    invasion_pat = re.compile('invasion')
    breslow_pat = re.compile('breslow')
    depth_pat = re.compile('depth')
    thick_pat = re.compile('thick')

    string = '  {}  '.format(string)
    string_chop = '  {}  '.format(string_chop)
    strings = [string_chop, string]            
        
    # if note exists, mark it's location
    note_pat = re.compile('note:')

    #### NEW PROTOCAL 190724
    for st in strings:
        
        
        # Which patterns exist in the string?
                        # No
        if type(pat_1.search(st)) == re.Match:
            explanation[0] = 1
        if type(pat_2.search(st)) == re.Match:
            explanation[1] = 1
        if type(pat_3.search(st)) == re.Match:
            explanation[2] = 1
        if type(pat_4.search(st)) == re.Match:
            explanation[3] = 1
        if type(pat_5.search(st)) == re.Match:
            explanation[4] = 1
        if type(pat_6.search(st)) == re.Match:
            explanation[5] = 1
        if type(pat_7.search(st)) == re.Match:
            explanation[6] = 1
        if type(pat_8.search(st)) == re.Match:
            explanation[7] = 1
        if type(pat_9.search(st)) == re.Match:
            explanation[8] = 1
        if type(pat_10.search(st)) == re.Match:
            explanation[9] = 1
        if type(pat_11.search(st)) == re.Match:
            explanation[10] = 1
        if type(pat_12.search(st)) == re.Match:
            explanation[11] = 1
                        # Maybe
        if type(pat_13.search(st)) == re.Match:
            explanation[12] = 1
        if type(pat_14.search(st)) == re.Match:
            explanation[13] = 1
        if type(pat_15.search(st)) == re.Match:
            explanation[14] = 1
        if type(pat_16.search(st)) == re.Match:
            explanation[15] = 1
        if type(pat_17.search(st)) == re.Match:
            explanation[16] = 1
        if type(pat_18.search(st)) == re.Match:
            explanation[17] = 1
        if type(pat_19.search(st)) == re.Match:
            explanation[18] = 1
        if type(pat_20.search(st)) == re.Match:
            explanation[19] = 1
        if type(pat_21.search(st)) == re.Match:
            explanation[20] = 1
        if type(pat_22.search(st)) == re.Match:
            explanation[21] = 1
        if type(pat_23.search(st)) == re.Match:
            explanation[22] = 1
        if type(pat_24.search(st)) == re.Match:
            explanation[23] = 1
        if type(pat_25.search(st)) == re.Match:
            explanation[24] = 1
        if type(pat_26.search(st)) == re.Match:
            explanation[25] = 1
        if type(pat_27.search(st)) == re.Match:
            explanation[26] = 1
        if type(pat_28.search(st)) == re.Match:
            explanation[27] = 1
        if type(pat_29.search(st)) == re.Match:
            explanation[28] = 1
        if type(pat_30.search(st)) == re.Match:
            explanation[29] = 1
        if type(pat_31.search(st)) == re.Match:
            explanation[30] = 1
        if type(pat_32.search(st)) == re.Match:
            explanation[31] = 1
        if type(pat_33.search(st)) == re.Match:
            explanation[32] = 1
        if type(pat_34.search(st)) == re.Match:
            explanation[33] = 1
        if type(pat_35.search(st)) == re.Match:
            explanation[34] = 1
        if type(pat_36.search(st)) == re.Match:
            explanation[35] = 1
        if type(pat_37.search(st)) == re.Match:
            explanation[36] = 1
        if type(pat_38.search(st)) == re.Match:
            explanation[37] = 1
        if type(pat_39.search(st)) == re.Match:
            explanation[38] = 1
        if type(pat_40.search(st)) == re.Match:
            explanation[39] = 1
        if type(pat_41.search(st)) == re.Match:
            explanation[40] = 1
        if type(pat_42.search(st)) == re.Match:
            explanation[41] = 1        
        # how does it specify INVASION?
        if type(invasive_pat.search(st)) == re.Match:
            invasion_list[0] = 1
        if type(invasion_pat.search(st)) == re.Match:
            invasion_list[1] = 1
        if type(breslow_pat.search(st)) == re.Match:
            invasion_list[2] = 1
        if type(depth_pat.search(st)) == re.Match:
            invasion_list[3] = 1
        if type(thick_pat.search(st)) == re.Match:
            invasion_list[4] = 1

        
        # Check for any Melanoma flag POSITIVE
        if any(item.replace(' ', '') in st.replace(' ', '') for item in mel):
            
            # make note of location
            location = dx_before_after_note(st, mel_pat, note_pat)
            
            # Check for In-Situ flag POSITIVE #################################
            if type(mel_flag_insitu_pat.search(st)) == re.Match:
                
                # if so, create two strings:
                # 1. the original string st
                # 2. the original string minus any instances of 'in situ melanoma'
                st_sub = re.sub(r'(melanoma (in situ|in-situ|insitu)|(in situ|insitu|in-situ) melanoma|lentigo maligna)', r'', st)
                st_sub = re.sub(r'\s{2,}', r' ', st_sub)
                st_sub = '  {}  '.format(st_sub)

                # In-Situ dx
                insitu_dx = no_AND_maybe_pat(st, mel_no_insitu_pat, mel_maybe_insitu_pat)              

                # Check if there is still a need to check for invasive dx
                if any(item.replace(' ', '') in st_sub.replace(' ', '') for item in at_least_insitu):

                    # Invasive dx
                    invasive_dx = no_AND_maybe_pat(st_sub, mel_no_invasive_pat, mel_maybe_invasive_pat)
                
                else:
                    # Invasive dx
                    invasive_dx = [0,0,'']

            # In-Situe flag NEGATIVE        
            else:
                # In-Situ dx
                insitu_dx = [0,0,'']

                # Invasive dx
                invasive_dx = no_AND_maybe_pat(st, mel_no_invasive_pat, mel_maybe_invasive_pat)

            # [mel, hard insitu, soft insitu, hard invasive, soft invasive]
            out = [0] + insitu_dx[0:2] + invasive_dx[0:2] + [insitu_dx[2]] + [invasive_dx[2]] + [location] + explanation + invasion_list
            out[0] = max(out[1:5])
            return(out)
            
        else:
            continue
    
    # if all else fails, return no mel
    return([0,0,0,0,0,'','', location] + explanation + invasion_list)


# will only work if the keyword shows up in the text
def dx_before_after_note(string, dx_pat, note_pat):
    dx_location = dx_pat.search(string).start()
    if type(note_pat.search(string)) == re.Match:
       note_location = note_pat.search(string).start()
    else:
        return('no note')
    if dx_location < note_location:
        return('before')
    else:
        return('after')


def breslow_thick(string):
    # clean string
    string = string.lower()
    # rid string of extra whitespaces
    string = re.sub(r'\s{2,}', r' ', string)
    # identify sentence in path dx section
    discover_pat = re.compile('((no thicker than |breslow thickness(|(| is) (approximately|at least))(:|)(| at least) |(invasive|depth|invasion)(|(| is) at least| component)( to| of)( | approximately ))([.]\d{1,2}|\d{1}(|.\d{1,2}))(mm| mm)|([.]\d{1,2}|\d{1}(|.\d{1,2}))(mm| mm) (thick|in thickness))')
    # if it doesn't exist, return empty string
    if type(discover_pat.search(string)) != re.Match:
        return('')
    substring = discover_pat.search(string).group(0)
    # return measurement
    return_pat = re.compile('([.]\d{1,2}|\d{1}(|.\d{1,2}))(mm| mm)')
    return(return_pat.search(substring).group(0).strip())


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


#intermediate = ['aimp', 'severe atypia', 'severely atypical', \
#                'severely dysplastic', 'atypical intraepidermal', \
#                'insufficient for outright', 'atypical intradermal mel', 'atypical junctional mel', \
#                'intradermal spitzoid melanocytic proliferation', \
#                'atypical melanocytic', 'intraepidermal melanocytic proliferation', \
#                'intraepidermal melanocytic dysplasia']

    
def no_pattern(keyword_expression):
    no_pat1 = '((\s|-|^\w)((free|absence) of|non-diagnositic|(fail|failed) to reveal|insufficient|negative|no|not)\s[^.;:()]*'
    no_pat2 = '[^.;:()]*(not (seen|identified)|negative))'
    paste = '{}{}|{}{}'.format(no_pat1, keyword_expression, keyword_expression, no_pat2)
    return(re.compile(paste))


def maybe_pattern(keyword_expression):
    maybe_pat1 = "(\s|^\w)(could be|border on|hesitate|possible|not unequivocally|(difficult to|not possible to|cannot|can't|can not)( | entirely )(exclude|rule out)|concerning|suspicious|worrisome|possibility|borderline)[^.]*"
    paste = '{}{}'.format(maybe_pat1, keyword_expression)
    return(re.compile(paste))


def nBeforeAfter(string, keyword, n):
    # return the n words before and n words after a specified keyword/phrase
        # clean up punctuation and extra whitespace in string
#    keyword_continuous = re.sub(r' ', r'', keyword)
#    string = re.sub(keyword, keyword_continuous, string)
    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    vnote = re.compile('(photo #:|vectra #:)')
    sitenote = re.compile(r'(:|;|-)')
    if type(vnote.search(string)) == re.Match:
        string = string[re.search(vnote, string).end():]
    elif type(sitenote.search(string)) == re.Match:    
        string = string[re.search(sitenote, string).end():]
        if type(sitenote.search(string)) == re.Match:
            string = string[re.search(sitenote, string).end():]
    string = string.translate(string.maketrans(dict.fromkeys(stringmod.punctuation)))
    string = re.sub(r'\s{2,}', r' ', string)
    string = string.strip()
    keypat = re.compile(keyword)
    while type(keypat.search(string)) == re.Match:
        keyword_start = re.search(keypat, string).start()
        keyword_end = re.search(keypat, string).end()
        string = '{}{}{}'.format(string[0:keyword_start],
                  'KEY',
                  string[keyword_end:])
    lis = string.split(' ')
    indexes = set([i for i in range(0, len(lis)) if lis[i] == 'KEY'])
    # initialize output
    Before = []
    After = []
    # determine the n words falling before and after
    for i in indexes:  
        for r in range(0, n):
            r += 1
            if (i-r) > -1:
                Before.append(lis[i-r])
            if (i+r) < len(lis):
                After.append(lis[i+r])
    return([Before, After])
    
    
def nGram(string, n):
    if string == '':
        return([])
    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    sitenote = re.compile(r'(:|;|-)')
    if type(sitenote.search(string)) == re.Match:
        string = string[re.search(sitenote, string).end():]
        if type(sitenote.search(string)) == re.Match:
            string = string[re.search(sitenote, string).end():]
    string = string.translate(string.maketrans(dict.fromkeys(stringmod.punctuation)))
    string = re.sub(r'\s{2,}', r' ', string)
    string = string.strip()
    lis = string.split(' ')
    # check if there are enough words to accomplish "n" grams
    if len(lis) < n:
        return([])
    # number of n-grams
    combos = len(lis) - n + 1
    # initiate output
    out = []
    for i in range(0,combos):
        # start building the ngram
        ngram_i = lis[i]
        for j in range(i + 1, i + n):
            ngram_i = '{} {}'.format(ngram_i, lis[j])
        out.append(ngram_i)
    return(out)


def allWords(string):
    if string == '':
        return([])
    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    sitenote = re.compile(r'(:|;|-)')
    if type(sitenote.search(string)) == re.Match:
        string = string[re.search(sitenote, string).end():]
        if type(sitenote.search(string)) == re.Match:
            string = string[re.search(sitenote, string).end():]
    string = string.translate(string.maketrans(dict.fromkeys(stringmod.punctuation)))
    string = re.sub(r'\s{2,}', r' ', string)
    string = string.strip()
    lis = string.split(' ')
    out = {}
    for i in range(0, len(lis)):
        if lis[i] not in out.keys():
            out[lis[i]] = 1
        else:
            out[lis[i]] += 1
    return(out)


def getfeatures():
    # iniate wordbanks
    # YES
    yes1 = 'apparent'
    yes2 = 'appears'
    yes3 = '(comparable|combatible|consistent) with'
    yes4 = 'favors'
    yes5 = '(most likely|presumed|probabile|suspect|typical of)'
    # NO
    no1 = '(free|absence) of'
    no2 = '(fail|failed) to reveal'
    no3 = 'insufficient'
    no4 = 'negative'
    no5 = 'no'
    no6 = 'not'
    no7 = 'not seen'
    no8 = '(not identified|non-diagnositic)'
    no9 = 'negative'
    # INCONCLUSIVE
    eh1 = '(could be|suggests)'
    eh2 = '(border on|borderline)'
    eh3 = '(hesitate|not unequivocally| equivocal )'
    eh4 = '(possible|possibility|potentially)'
    eh5 = "(difficult to|not possible to|cannot|can't|cannot|can not)(| entirely) (exclude|rule out)"
    eh6 = '(concerning|questionable|suspicious)'
    eh7 = 'worrisome'
    # MEL
    mel1 = 'melanoma'
    mel2 = 'insitu'
    mel3 = '(invasive|invasion)'
    mel4 = '(breslow|depth|thick)'
    # LENTIGO
    len1 = 'lentigo'
    # AIMP
    aimp1 = '(aimp|pimp|sumpus|meltump|(atypical|pagetoid)(| intraepithelial| intradermal| intraepidermal) melanocytic (neoplasm|proliferation)|melanocytic tumor[^.]*uncertain(| malignant) potential)'
    # Atyp Spitz
    atypspit1 = 'atypical spitzoid lesion'
    # Spitz
    spit1 = '(spitz|spindle cell)'
    # Atypia
    atyp1 = '(atypia|atypical|dysplastic|dysplasia)'
    # Nevus
    nev1 = '(nevus|nevi)'
    nev2 = 'melanocytic proliferation'
    
    keybank = [yes1, yes2, yes3, yes4, yes5, no1, no2, no3, no4, no5, no6, no7, no8, no9, 
               eh1, eh2, eh3, eh4, eh5, eh6, eh7,
               mel1, mel2, mel3, mel4, len1, aimp1, atypspit1, spit1, atyp1, nev1, nev2,
               'bcc', 'basal cell carcinoma', 'scc', 'sqamous cell carcinoma']

    bigbank = {}
    beforebank = {}
    afterbank = {}
    for k in keybank:
        beforebank[k] = {}    
    for k in keybank:
        afterbank[k] = {}    
    n_beforeafter = 5
    grambank = {2:{}, 3:{}, 4:{}}
    
    # Establish directory and read dataline table
    fn = "DataLine Results - MED18416 - 20190710 12.09.59.xlsx"
    xls = ps.ExcelFile(fn)
    data = xls.parse("Results 1", skiprows=5, index_col = None)
    
    # filter out all but the GENERAL MEDICINE reports
    data = data[data['Doctor Service'] == 'GENERAL MEDICINE']
    data.reset_index(drop=True, inplace=True)
    for r in range(0, len(data)):
    #for r in range(0, 50):
        #if data['Accession No'][r] == 'S18-21729': 
        #    print(r, data['Accession No'][r])
        print(r, data['Accession No'][r])
        ###########################################################################
        # identify:
        #   number of lesions in the report
        #   clinical dx and patient history section
        #   pathological dx section
        ###########################################################################
        pathrpt = data['Report Text'][r]
        pathrpt = pathrpt.lower().strip()
    
        lesions_no = number_les_in_report(pathrpt)
        clin_r = clinical_dx_section(pathrpt)
        if clin_r == None:
            clin_r = ''
        spec_r = spec_submit_section(pathrpt)
        if spec_r == None:
            spec_r = ''
        path = path_dx_section(pathrpt)
        if path == None:
            path = ''
        ###########################################################################
        # if only one lesion in the report
        ###########################################################################
        if lesions_no == 1:
            path_r = lesion_r_path(path)
            allwords_r = allWords(path_r)
            for k in allwords_r.keys():
                if k not in bigbank.keys():
                    bigbank[k] = 1
                else:
                    bigbank[k] += allwords_r[k]
                    
            for n_ngram in grambank.keys():
                ngram_r = nGram(path_r, n_ngram)
                count_k = 0
                for k in ngram_r:
                    if k not in grambank[n_ngram].keys():
                        grambank[n_ngram][k] = 1
                        continue
                    else:
                        count_k += 1
                grambank[n_ngram][k] = count_k
                
            for word in beforebank.keys():
                nbeforeafter_r = nBeforeAfter(path_r, word, n_beforeafter)
                for k in nbeforeafter_r[0]:
                    if k not in beforebank[word].keys():
                        beforebank[word][k] = 1
                    else:
                        beforebank[word][k] += 1
                    
                for k in nbeforeafter_r[1]:
                    if k not in afterbank[word].keys():
                        afterbank[word][k] = 1
                    else:
                        afterbank[word][k] += 1

            continue
     
        ###########################################################################
        # if multiple lesions in the report...
        ###########################################################################
        for les in range(1, lesions_no + 1):
            path_i = lesion_i_path(les, path)
            allwords_i = allWords(path_i)
            for k in allwords_i.keys():
                if k not in bigbank.keys():
                    bigbank[k] = 1
                else:
                    bigbank[k] += allwords_i[k]

            for n_ngram in grambank.keys():
                ngram_i = nGram(path_i, n_ngram)
                count_k = 0
                for k in ngram_i:
                    if k not in grambank[n_ngram].keys():
                        grambank[n_ngram][k] = 1
                        continue
                    else:
                        count_k += 1
                grambank[n_ngram][k] = count_k
            
            for word in beforebank.keys():
                nbeforeafter_i = nBeforeAfter(path_i, word, n_beforeafter)
                for k in nbeforeafter_i[0]:
                    if k not in beforebank[word].keys():
                        beforebank[word][k] = 1
                    else:
                        beforebank[word][k] += 1
                    
                for k in nbeforeafter_i[1]:
                    if k not in afterbank[word].keys():
                        afterbank[word][k] = 1
                    else:
                        afterbank[word][k] += 1
    ###########################################################################
    
    # OUTPUT THE WORDBANK
    p99 = np.percentile(list(bigbank.values()), 99)
    filt_bigbank = {k:v for k,v in bigbank.items() if v >= p99}
    # creat csv
    out_bigbank = list(zip(filt_bigbank.keys(), filt_bigbank.values()))
    out_bigbank = ps.DataFrame(out_bigbank, columns = ['word', 'count'])
    out_bigbank.to_csv('wordBank_20190819.csv')
    
    # OUTPUT THE NGRAM DATA
    filt_grambank = {}
    for ngram in grambank.keys():
        # 99th percentile for counts
        p99 = np.percentile(list(grambank[ngram].values()), 99)
        # filtered dictionary
        filt_grambank[ngram] = {k:v for k,v in grambank[ngram].items() if v >= p99}
    # create csv
    ngram_n_csv = []
    ngram_k_csv = []
    ngram_v_csv = []
    for ngram in filt_grambank.keys():
        ngram_n = [ngram] * len(filt_grambank[ngram])
        ngram_n_csv = ngram_n_csv + ngram_n
        ngram_k_csv = ngram_k_csv + list(filt_grambank[ngram].keys())
        ngram_v_csv = ngram_v_csv + list(filt_grambank[ngram].values())
    out_ngram = list(zip(ngram_n_csv, ngram_k_csv, ngram_v_csv))
    out_ngram = ps.DataFrame(out_ngram, columns = ['gram', 'key', 'count'])
    out_ngram.to_csv("nGram_20190819.csv")

    # OUTPUT THE BEFORE/AFTER TABLE
    filt_beforebank = {}
    for word in beforebank.keys():
        # check if the value is empty
        if beforebank[word] == {}:
            continue
        # 99th percentile for counts
        p99 = np.percentile(list(beforebank[word].values()), 99)
        # filtered dictionary
        filt_beforebank[word] = {k:v for k,v in beforebank[word].items() if v >= p99}
    filt_afterbank = {}
    for word in afterbank.keys():
        # check if the value is empty
        if afterbank[word] == {}:
            continue
        # 99th percentile for counts
        p99 = np.percentile(list(afterbank[word].values()), 99)
        # filtered dictionary
        filt_afterbank[word] = {k:v for k,v in afterbank[word].items() if v >= p99}
    # create csv
    bank_location_csv = []
    bank_word_csv = []
    bank_k_csv = []
    bank_v_csv = []
    for word in filt_beforebank.keys():
        location_vector = ['before'] * len(filt_beforebank[word])
        bank_location_csv = bank_location_csv + location_vector
        word_vector = [word] * len(filt_beforebank[word])
        bank_word_csv = bank_word_csv + word_vector
        bank_k_csv = bank_k_csv + list(filt_beforebank[word].keys())
        bank_v_csv = bank_v_csv + list(filt_beforebank[word].values())
    for word in filt_afterbank.keys():
        location_vector = ['after'] * len(filt_afterbank[word])
        bank_location_csv = bank_location_csv + location_vector
        word_vector = [word] * len(filt_afterbank[word])
        bank_word_csv = bank_word_csv + word_vector
        bank_k_csv = bank_k_csv + list(filt_afterbank[word].keys())
        bank_v_csv = bank_v_csv + list(filt_afterbank[word].values())
    out_beforeafter = list(zip(bank_location_csv, bank_word_csv, bank_k_csv, bank_v_csv))
    out_beforeafter = ps.DataFrame(out_beforeafter, columns = ['location', 'keyword', 'closeword', 'count'])
    out_beforeafter.to_csv('beforeAfter_20190819.csv')


def main():
    # Establish directory and read dataline table
    fn = "DataLine Results - MED18416 - 20190710 12.09.59.xlsx"
    xls = ps.ExcelFile(fn)
    data = xls.parse("Results 1", skiprows=5, index_col = None)
    
    # filter out all but the GENERAL MEDICINE reports
    data = data[data['Doctor Service'] == 'GENERAL MEDICINE']
    data.reset_index(drop=True, inplace=True)
    
    # initiate table
    Accession = []
    MRN = []
    Date = []
    DaysReportMinusProc = []
    Lesion = []
    Vectra = []
    Site = []
    ClinDx = []
    PathDx = []
    #
    PathDxLength = []   # analyzing relationship of number of chars with accuracy, dx, etc.
    #
    DxGroup = []
    DxText = []
    MelDx = []
    InSituDxHard = []
    InSituDxSoft = []
    InvasiveDxHard = []
    InvasiveDxSoft = []
    InSituText = []
    InvasiveText = []
    Breslow = []
    #
    dx_location = []
    #
    pat1 = []
    pat2 = []
    pat3 = []
    pat4 = []
    pat5 = []
    pat6 = []
    pat7 = []
    pat8 = []
    pat9 = []
    pat10 = []
    pat11 = []
    pat12 = []
    pat13 = []
    pat14 = []
    pat15 = []
    pat16 = []
    pat17 = []
    pat18 = []
    pat19 = []
    pat20 = []
    pat21 = []
    pat22 = []
    pat23 = []
    pat24 = []
    pat25 = []
    pat26 = []
    pat27 = []
    pat28 = []
    pat29 = []
    pat30 = []
    pat31 = []
    pat32 = []
    pat33 = []
    pat34 = []
    pat35 = []
    pat36 = []
    pat37 = []
    pat38 = []
    pat39 = []
    pat40 = []
    pat41 = []
    pat42 = []
    #
    invasive1 = []
    invasive2 = []
    invasive3 = []
    invasive4 = []
    invasive5 = []
    #
    MPATH_DIAGNOGIS = []
    MPATH_HARD = []
    MPATH_SOFT = []
    MPATH_SECONDGUESS = []
    
    # NO
    pat_1 = re.compile('(\s|-|^\w)(free of)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_2 = re.compile('(\s|-|^\w)absence of\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_3 = re.compile('(\s|-|^\w)(non-diagnositic)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_4 = re.compile('(\s|-|^\w)(fail to reveal)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_5 = re.compile('(\s|-|^\w)(failed to reveal)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_6 = re.compile('(\s|-|^\w)(insufficient)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_7 = re.compile('(\s|-|^\w)(negative)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_8 = re.compile('(\s|-|^\w)(no)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_9 = re.compile('(\s|-|^\w)(not)\s[^.;:()]*(melanoma|lentigo maligna)')
    pat_10 = re.compile('(\s|-|^\w)(melanoma|lentigo maligna)[^.;:()]*(not seen)')
    pat_11 = re.compile('(\s|-|^\w)(melanoma|lentigo maligna)[^.;:()]*(not identified)')
    pat_12 = re.compile('(\s|-|^\w)(melanoma|lentigo maligna)[^.;:()]*(negative)')
    # INCONCLUSIVE
    pat_13 = re.compile('(\s|^\w)(could be)[^.]*(melanoma|lentigo maligna)')
    pat_14 = re.compile('(\s|^\w)(border on)[^.]*(melanoma|lentigo maligna)')
    pat_15 = re.compile('(\s|^\w)(hesitate)[^.]*(melanoma|lentigo maligna)')
    pat_16 = re.compile('(\s|^\w)(possible)[^.]*(melanoma|lentigo maligna)')
    pat_17 = re.compile('(\s|^\w)(not unequivocally)[^.]*(melanoma|lentigo maligna)')
    pat_18 = re.compile('(\s|^\w)(difficult to entirely exclude)[^.]*(melanoma|lentigo maligna)')
    pat_19 = re.compile('(\s|^\w)(difficult to exclude)[^.]*(melanoma|lentigo maligna)')
    pat_20 = re.compile('(\s|^\w)(difficult to entirely rule out)[^.]*(melanoma|lentigo maligna)')
    pat_21 = re.compile('(\s|^\w)(difficult to rule out)[^.]*(melanoma|lentigo maligna)')
    pat_22 = re.compile('(\s|^\w)(not possible to entirely exclude)[^.]*(melanoma|lentigo maligna)')
    pat_23 = re.compile('(\s|^\w)(not possible to exclude)[^.]*(melanoma|lentigo maligna)')
    pat_24 = re.compile('(\s|^\w)(not possible to entirely rule out)[^.]*(melanoma|lentigo maligna)')
    pat_25 = re.compile('(\s|^\w)(not possible to rule out)[^.]*(melanoma|lentigo maligna)')
    pat_26 = re.compile("(\s|^\w)(cannot entirely exclude)[^.]*(melanoma|lentigo maligna)")
    pat_27 = re.compile("(\s|^\w)(cannot exclude)[^.]*(melanoma|lentigo maligna)")
    pat_28 = re.compile("(\s|^\w)(cannot entirely rule out)[^.]*(melanoma|lentigo maligna)")
    pat_29 = re.compile("(\s|^\w)(cannot rule out)[^.]*(melanoma|lentigo maligna)")
    pat_30 = re.compile("(\s|^\w)(can't entirely exclude)[^.]*(melanoma|lentigo maligna)")
    pat_31 = re.compile("(\s|^\w)(can't exclude)[^.]*(melanoma|lentigo maligna)")
    pat_32 = re.compile("(\s|^\w)(can't entirely rule out)[^.]*(melanoma|lentigo maligna)")
    pat_33 = re.compile("(\s|^\w)(can't rule out)[^.]*(melanoma|lentigo maligna)")
    pat_34 = re.compile("(\s|^\w)(can not entirely exclude)[^.]*(melanoma|lentigo maligna)")
    pat_35 = re.compile("(\s|^\w)(can not exclude)[^.]*(melanoma|lentigo maligna)")
    pat_36 = re.compile("(\s|^\w)(can not entirely rule out)[^.]*(melanoma|lentigo maligna)")
    pat_37 = re.compile("(\s|^\w)(can not rule out)[^.]*(melanoma|lentigo maligna)")
    pat_38 = re.compile('(\s|^\w)(concerning)[^.]*(melanoma|lentigo maligna)')
    pat_39 = re.compile('(\s|^\w)(suspicious)[^.]*(melanoma|lentigo maligna)')
    pat_40 = re.compile('(\s|^\w)(worrisome)[^.]*(melanoma|lentigo maligna)')
    pat_41 = re.compile('(\s|^\w)(possibility)[^.]*(melanoma|lentigo maligna)')
    pat_42 = re.compile('(\s|^\w)(borderline)[^.]*(melanoma|lentigo maligna)')

    
    for r in range(0, len(data)):
    #for r in range(0, 50):
        #if data['Accession No'][r] == 'S18-21729': 
        #    print(r, data['Accession No'][r])
        print(r, data['Accession No'][r])
        ###########################################################################
        # identify:
        #   number of lesions in the report
        #   clinical dx and patient history section
        #   pathological dx section
        ###########################################################################
        pathrpt = data['Report Text'][r]
        pathrpt = pathrpt.lower().strip()
    
        lesions_no = number_les_in_report(pathrpt)
        clin_r = clinical_dx_section(pathrpt)
        if clin_r == None:
            clin_r = ''
        spec_r = spec_submit_section(pathrpt)
        if spec_r == None:
            spec_r = ''
        path = path_dx_section(pathrpt)
        if path == None:
            path = ''
        ###########################################################################
        # if only one lesion in the report
        ###########################################################################
        if lesions_no == 1:
            Accession.append(data['Accession No'][r])
            MRN.append(data['MRN'][r])
            Date.append(data['Report Date'][r])
            DaysReportMinusProc.append(days_since_collecting_report(pathrpt))
            # Simple. The lesion #
            Lesion.append(1)
            Site.append(les_site_i(1, spec_r))
            ClinDx.append(clin_r.replace('\r\n', ''))
            path_r = lesion_r_path(path)

            PathDx.append(path_r.replace('\r\n', ''))
            PathDxLength.append(len(path_r))
            if vectra_n(path_r) != '':
                Vectra.append(vectra_n(path_r))      
            else:
                Vectra.append(vectra_n(les_site_i(1, spec_r)))
            dxgroup_r = dx_group(path_r)
            DxGroup.append(dxgroup_r[0])
            DxText.append(dxgroup_r[1])
            
            melclass_r = melanoma_DX(path_r, pat_1, pat_2, pat_3, pat_4, pat_5, pat_6, pat_7, pat_8, pat_9, pat_10, pat_11, pat_12, pat_13, pat_14, pat_15, pat_16, pat_17, pat_18, pat_19, pat_20, pat_21, pat_22, pat_23, pat_24, pat_25, pat_26, pat_27, pat_28, pat_29, pat_30, pat_31, pat_32, pat_33, pat_34, pat_35, pat_36, pat_37, pat_38, pat_39, pat_40, pat_41, pat_42)

            MelDx.append(melclass_r[0])
            InSituDxHard.append(melclass_r[1])
            InSituDxSoft.append(melclass_r[2])
            InvasiveDxHard.append(melclass_r[3])
            InvasiveDxSoft.append(melclass_r[4])
            InSituText.append(melclass_r[5])
            InvasiveText.append(melclass_r[6])

            dx_location.append(melclass_r[7])
            Breslow.append(breslow_thick(path_r))
            #
            pat1.append(melclass_r[8])
            pat2.append(melclass_r[9])
            pat3.append(melclass_r[10])
            pat4.append(melclass_r[11])
            pat5.append(melclass_r[12])
            pat6.append(melclass_r[13])
            pat7.append(melclass_r[14])
            pat8.append(melclass_r[15])
            pat9.append(melclass_r[16])
            pat10.append(melclass_r[17])
            pat11.append(melclass_r[18])
            pat12.append(melclass_r[19])
            pat13.append(melclass_r[20])
            pat14.append(melclass_r[21])
            pat15.append(melclass_r[22])
            pat16.append(melclass_r[23])
            pat17.append(melclass_r[24])
            pat18.append(melclass_r[25])
            pat19.append(melclass_r[26])
            pat20.append(melclass_r[27])
            pat21.append(melclass_r[28])
            pat22.append(melclass_r[29])
            pat23.append(melclass_r[30])
            pat24.append(melclass_r[31])
            pat25.append(melclass_r[32])
            pat26.append(melclass_r[33])
            pat27.append(melclass_r[34])
            pat28.append(melclass_r[35])
            pat29.append(melclass_r[36])
            pat30.append(melclass_r[37])
            pat31.append(melclass_r[38])
            pat32.append(melclass_r[39])
            pat33.append(melclass_r[40])
            pat34.append(melclass_r[41])
            pat35.append(melclass_r[42])
            pat36.append(melclass_r[43])
            pat37.append(melclass_r[44])
            pat38.append(melclass_r[45])
            pat39.append(melclass_r[46])
            pat40.append(melclass_r[47])
            pat41.append(melclass_r[48])
            pat42.append(melclass_r[49])
            #
            invasive1.append(melclass_r[50])
            invasive2.append(melclass_r[51])
            invasive3.append(melclass_r[52])
            invasive4.append(melclass_r[53])
            invasive5.append(melclass_r[54])

            mpath_decision = MPATH_dx(path_r)
            MPATH_DIAGNOGIS.append(mpath_decision[0])
            MPATH_HARD.append(mpath_decision[1])
            MPATH_SOFT.append(mpath_decision[2])
            MPATH_SECONDGUESS.append(mpath_decision[3])

            continue
     
        ###########################################################################
        # if multiple lesions in the report...
        ###########################################################################
        for les in range(1, lesions_no + 1):
           
            # This is the easy stuff b/c it is the same for all lesions
            Accession.append(data['Accession No'][r])
            MRN.append(data['MRN'][r])
            Date.append(data['Report Date'][r])     
            DaysReportMinusProc.append(days_since_collecting_report(pathrpt))
            # Simple. The lesion #
            Lesion.append(les)
            Site.append(les_site_i(les, spec_r))

            # since clinical dx and history is a messy field, just use clin_R
            ClinDx.append(clin_r)
            path_i = lesion_i_path(les, path)
            PathDx.append(path_i)
            PathDxLength.append(len(path_i))
            if vectra_n(path_i) != '':
                Vectra.append(vectra_n(path_i))      
            else:
                Vectra.append(vectra_n(les_site_i(les, spec_r)))
            dxgroup_i = dx_group(path_i)            
            DxGroup.append(dxgroup_i[0])
            DxText.append(dxgroup_i[1])
            
            melclass_i = melanoma_DX(path_i, pat_1, pat_2, pat_3, pat_4, pat_5, pat_6, pat_7, pat_8, pat_9, pat_10, pat_11, pat_12, pat_13, pat_14, pat_15, pat_16, pat_17, pat_18, pat_19, pat_20, pat_21, pat_22, pat_23, pat_24, pat_25, pat_26, pat_27, pat_28, pat_29, pat_30, pat_31, pat_32, pat_33, pat_34, pat_35, pat_36, pat_37, pat_38, pat_39, pat_40, pat_41, pat_42)

            MelDx.append(melclass_i[0])
            InSituDxHard.append(melclass_i[1])
            InSituDxSoft.append(melclass_i[2])
            InvasiveDxHard.append(melclass_i[3])
            InvasiveDxSoft.append(melclass_i[4])
            InSituText.append(melclass_i[5])
            InvasiveText.append(melclass_i[6])

            dx_location.append(melclass_i[7])
            
            Breslow.append(breslow_thick(path_i))
            #
            pat1.append(melclass_i[8])
            pat2.append(melclass_i[9])
            pat3.append(melclass_i[10])
            pat4.append(melclass_i[11])
            pat5.append(melclass_i[12])
            pat6.append(melclass_i[13])
            pat7.append(melclass_i[14])
            pat8.append(melclass_i[15])
            pat9.append(melclass_i[16])
            pat10.append(melclass_i[17])
            pat11.append(melclass_i[18])
            pat12.append(melclass_i[19])
            pat13.append(melclass_i[20])
            pat14.append(melclass_i[21])
            pat15.append(melclass_i[22])
            pat16.append(melclass_i[23])
            pat17.append(melclass_i[24])
            pat18.append(melclass_i[25])
            pat19.append(melclass_i[26])
            pat20.append(melclass_i[27])
            pat21.append(melclass_i[28])
            pat22.append(melclass_i[29])
            pat23.append(melclass_i[30])
            pat24.append(melclass_i[31])
            pat25.append(melclass_i[32])
            pat26.append(melclass_i[33])
            pat27.append(melclass_i[34])
            pat28.append(melclass_i[35])
            pat29.append(melclass_i[36])
            pat30.append(melclass_i[37])
            pat31.append(melclass_i[38])
            pat32.append(melclass_i[39])
            pat33.append(melclass_i[40])
            pat34.append(melclass_i[41])
            pat35.append(melclass_i[42])
            pat36.append(melclass_i[43])
            pat37.append(melclass_i[44])
            pat38.append(melclass_i[45])
            pat39.append(melclass_i[46])
            pat40.append(melclass_i[47])
            pat41.append(melclass_i[48])
            pat42.append(melclass_i[49])
            #
            invasive1.append(melclass_i[50])
            invasive2.append(melclass_i[51])
            invasive3.append(melclass_i[52])
            invasive4.append(melclass_i[53])
            invasive5.append(melclass_i[54])

            mpath_decision = MPATH_dx(path_i)
            MPATH_DIAGNOGIS.append(mpath_decision[0])
            MPATH_HARD.append(mpath_decision[1])
            MPATH_SOFT.append(mpath_decision[2])
            MPATH_SECONDGUESS.append(mpath_decision[3])


    # column bind all lists of data into a table    
    table = list(zip(Accession, MRN, Date, DaysReportMinusProc, Lesion, Vectra, Site, ClinDx, PathDx, PathDxLength, DxGroup, DxText, MelDx, InSituDxHard, InSituDxSoft, InvasiveDxHard, InvasiveDxSoft, Breslow, InSituText, InvasiveText, dx_location, pat1, pat2, pat3, pat4, pat5, pat6, pat7, pat8, pat9, pat10, pat11, pat12, pat13, pat14, pat15, pat16, pat17, pat18, pat19, pat20, pat21, pat22, pat23, pat24, pat25, pat26, pat27, pat28, pat29, pat30, pat31, pat32, pat33, pat34, pat35, pat36, pat37, pat38, pat39, pat40, pat41, pat42, invasive1, invasive2, invasive3, invasive4, invasive5, MPATH_DIAGNOGIS, MPATH_HARD, MPATH_SOFT, MPATH_SECONDGUESS))
    output = ps.DataFrame(table, columns = ['AccessionNo', 'MRN', 'ReportDate', 'DaysToReceiveReport', 'Lesion', 'Vectra', 'Site', 'ClinDx', 'PathDx', 'PathDxLength', 'MelEvolvedNevus', 'Evidence', 'MelPositive', 'InSituHard', 'InSituSoft', 'InvasiveHard', 'InvasiveSoft', 'BreslowThickness', 'InSituText', 'InvasiveText', 'dx_location', 'no1', 'no2', 'no3', 'no4', 'no5', 'no6', 'no7', 'no8', 'no9', 'no10', 'no11', 'no12', 'inconclusive1', 'inconclusive2', 'inconclusive3', 'inconclusive4', 'inconclusive5', 'inconclusive6', 'inconclusive7', 'inconclusive8', 'inconclusive9', 'inconclusive10', 'inconclusive11', 'inconclusive12', 'inconclusive13', 'inconclusive14', 'inconclusive15', 'inconclusive16', 'inconclusive17', 'inconclusive18', 'inconclusive19', 'inconclusive20', 'inconclusive21', 'inconclusive22', 'inconclusive23', 'inconclusive24', 'inconclusive25', 'inconclusive26', 'inconclusive27', 'inconclusive28', 'inconclusive29', 'inconclusive30', 'invasive1', 'invasive2', 'invasive3', 'invasive4', 'invasive5', 'MPATH_dx', 'MPATH_hard', 'MPATH_soft', 'MPATH_secondGuess'])
    output.to_csv("PathRptStudy_comprehensiveData_20190815.csv")




## run program
#if __name__ == "__main__":
#    main()

