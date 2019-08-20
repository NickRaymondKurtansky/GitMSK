########################################################################
#   Project: MPATH Dx using regex methods
#   Author: Nick Kurtansky
#   Date: 8/20/2019
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

    
def no_pattern(keyword_expression):
    no_pat1 = '((\s|-|^\w)((free|absence) of|non-diagnositic|(fail|failed) to reveal|insufficient|negative|no|not)\s[^.;:()]*'
    no_pat2 = '[^.;:()]*(not (seen|identified)|negative))'
    paste = '{}{}|{}{}'.format(no_pat1, keyword_expression, keyword_expression, no_pat2)
    return(re.compile(paste))


def maybe_pattern(keyword_expression):
    maybe_pat1 = "(\s|^\w)(could be|border on|hesitate|possible|not unequivocally|(difficult to|not possible to|cannot|can't|can not)( | entirely )(exclude|rule out)|concerning|suspicious|worrisome|possibility|borderline)[^.]*"
    paste = '{}{}'.format(maybe_pat1, keyword_expression)
    return(re.compile(paste))


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
    PathDxLength = []   # analyzing relationship of number of chars with accuracy, dx, etc.
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
            Breslow.append(breslow_thick(path_r))

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
            Breslow.append(breslow_thick(path_i))

    # column bind all lists of data into a table    
    table = list(zip(Accession, MRN, Date, DaysReportMinusProc, Lesion, Vectra, Site, ClinDx, PathDx, PathDxLength, Breslow))
    output = ps.DataFrame(table, columns = ['AccessionNo', 'MRN', 'ReportDate', 'DaysToReceiveReport', 'Lesion', 'Vectra', 'Site', 'ClinDx', 'PathDx', 'PathDxLength', 'BreslowThickness'])
    output.to_csv("MPATHclass_20190820.csv")




## run program
#if __name__ == "__main__":
#    main()

