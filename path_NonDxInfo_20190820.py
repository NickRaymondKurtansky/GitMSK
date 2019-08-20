########################################################################
#   Title: Path Report Dx
#   Author: Nick Kurtansky
#   Date: 8/19/2019
#
#   Contains all functions required to pull NON-DIAGNOSTIC information
#   from a set of histological reports
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
            dxgroup_r = dx_group(path_r)
            DxGroup.append(dxgroup_r[0])
            DxText.append(dxgroup_r[1])
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
            dxgroup_i = dx_group(path_i)            
            DxGroup.append(dxgroup_i[0])
            DxText.append(dxgroup_i[1])          
            Breslow.append(breslow_thick(path_i))
            

    # column bind all lists of data into a table    
    table = list(zip(Accession, MRN, Date, DaysReportMinusProc, Lesion, Vectra, Site, ClinDx, PathDx, PathDxLength, Breslow))
    output = ps.DataFrame(table, columns = ['AccessionNo', 'MRN', 'ReportDate', 'DaysToReceiveReport', 'Lesion', 'Vectra', 'Site', 'ClinDx', 'PathDx', 'PathDxLength', 'BreslowThickness'])
    output.to_csv("pathReportOnly_20190815.csv")




## run program
#if __name__ == "__main__":
#    main()

