########################################################################
#
#   Title: Feature Generation - functions and csv creation
#   Author: Nick Kurtansky
#   Date: 8/19/2019
#
#   functions: 
#       nBeforeAfter(string, keyword, n)
#           returns 2 lists - n words before and after each instance of a keyword/regex expression
#       nGram(string, n)
#           returns list of ngrams that appear in a string
#       allWords(string)
#           returns dictionary wordcount from string
#       main()
#           produces csv files
#           count of occurances for keywords, regular expressions, and ngrams
#           includes only those in teh 99th percentile of occurance
########################################################################


import statistics
import os
import pandas as ps
import re
import numpy as np
import datetime
import string as stringmod



###############################################################################

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



###############################################################################



def nBeforeAfter(string, keyword, n):
    # concatenate in situ
    string = re.sub(r'in( |-)situ', r'insitu', string)
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
    # concatenate in situ
    string = re.sub(r'in( |-)situ', r'insitu', string)
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
    # concatenate in situ
    string = re.sub(r'in( |-)situ', r'insitu', string)
    # Most DIAGNOSIS sections begin with site, which can be problematic,
    #   especially if that site is listed as "near melanoma scar"... and the 
    #   true dx is something other than melanoma.
    # To counter this, FIRST try from the end of the site note.
    sitenote = re.compile(r'(:|;|-)')

    if type(sitenote.search(string)) == re.Match:
        string = string[re.search(sitenote, string).end():]
        if type(sitenote.search(string)) == re.Match:
            string = string[re.search(sitenote, string).end():]
    string = re.sub(r'/', r' ', string)
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


def main():
#    # iniate wordbanks
#    # YES
#    yes1 = 'apparent'
#    yes2 = 'appears'
#    yes3 = '(comparable|combatible|consistent) with'
#    yes4 = 'favors'
#    yes5 = '(most likely|presumed|probabile|suspect|typical of)'
#    # NO
#    no1 = '(free|absence) of'
#    no2 = '(fail|failed) to reveal'
#    no3 = 'insufficient'
#    no4 = 'negative'
#    no5 = 'no'
#    no6 = 'not'
#    no7 = 'not seen'
#    no8 = '(not identified|non-diagnositic)'
#    no9 = 'negative'
#    # INCONCLUSIVE
#    eh1 = '(could be|suggests)'
#    eh2 = '(border on|borderline)'
#    eh3 = '(hesitate|not unequivocally| equivocal )'
#    eh4 = '(possible|possibility|potentially)'
#    eh5 = "(difficult to|not possible to|cannot|can't|cannot|can not)(| entirely) (exclude|rule out)"
#    eh6 = '(concerning|questionable|suspicious)'
#    eh7 = 'worrisome'
#    # MEL
#    mel1 = 'melanoma'
#    mel2 = 'insitu'
#    mel3 = '(invasive|invasion)'
#    mel4 = '(breslow|depth|thick)'
#    # LENTIGO
#    len1 = 'lentigo'
#    # AIMP
#    aimp1 = '(aimp|pimp|sumpus|meltump|(atypical|pagetoid)(| intraepithelial| intradermal| intraepidermal) melanocytic (neoplasm|proliferation)|melanocytic tumor[^.]*uncertain(| malignant) potential)'
#    # Atyp Spitz
#    atypspit1 = 'atypical spitzoid lesion'
#    # Spitz
#    spit1 = '(spitz|spindle cell)'
#    # Atypia
#    atyp1 = '(atypia|atypical|dysplastic|dysplasia)'
#    # Nevus
#    nev1 = '(nevus|nevi)'
#    nev2 = 'melanocytic proliferation'
#    
#    keybank = [yes1, yes2, yes3, yes4, yes5, no1, no2, no3, no4, no5, no6, no7, no8, no9, 
#               eh1, eh2, eh3, eh4, eh5, eh6, eh7,
#               mel1, mel2, mel3, mel4, len1, aimp1, atypspit1, spit1, atyp1, nev1, nev2,
#               'bcc', 'basal cell carcinoma', 'scc', 'sqamous cell carcinoma']
#
#    bigbank = {}
#    beforebank = {}
#    afterbank = {}
#    for k in keybank:
#        beforebank[k] = {}    
#    for k in keybank:
#        afterbank[k] = {}    
#    n_beforeafter = 5
#    grambank = {2:{}, 3:{}, 4:{}}
#    
#    # Establish directory and read dataline table
#    fn = "\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\DataLine Results - MED18416 - 20190710 12.09.59.xlsx"
#    xls = ps.ExcelFile(fn)
#    data = xls.parse("Results 1", skiprows=5, index_col = None)
#    
#    # filter out all but the GENERAL MEDICINE reports
#    data = data[data['Doctor Service'] == 'GENERAL MEDICINE']
#    data.reset_index(drop=True, inplace=True)
#    for r in range(0, len(data)):
#    #for r in range(0, 50):
#        #if data['Accession No'][r] == 'S18-21729': 
#        #    print(r, data['Accession No'][r])
#        print(r, data['Accession No'][r])
#        ###########################################################################
#        # identify:
#        #   number of lesions in the report
#        #   clinical dx and patient history section
#        #   pathological dx section
#        ###########################################################################
#        pathrpt = data['Report Text'][r]
#        pathrpt = pathrpt.lower().strip()
#    
#        lesions_no = number_les_in_report(pathrpt)
#        clin_r = clinical_dx_section(pathrpt)
#        if clin_r == None:
#            clin_r = ''
#        spec_r = spec_submit_section(pathrpt)
#        if spec_r == None:
#            spec_r = ''
#        path = path_dx_section(pathrpt)
#        if path == None:
#            path = ''
#        ###########################################################################
#        # if only one lesion in the report
#        ###########################################################################
#        if lesions_no == 1:
#            path_r = lesion_r_path(path)
#            allwords_r = allWords(path_r)
#            for k in allwords_r.keys():
#                if k not in bigbank.keys():
#                    bigbank[k] = 1
#                else:
#                    bigbank[k] += allwords_r[k]
#                    
#            for n_ngram in grambank.keys():
#                ngram_r = nGram(path_r, n_ngram)
#                count_k = 0
#                for k in ngram_r:
#                    if k not in grambank[n_ngram].keys():
#                        grambank[n_ngram][k] = 1
#                        continue
#                    else:
#                        count_k += 1
#                grambank[n_ngram][k] = count_k
#                
#            for word in beforebank.keys():
#                nbeforeafter_r = nBeforeAfter(path_r, word, n_beforeafter)
#                for k in nbeforeafter_r[0]:
#                    if k not in beforebank[word].keys():
#                        beforebank[word][k] = 1
#                    else:
#                        beforebank[word][k] += 1
#                    
#                for k in nbeforeafter_r[1]:
#                    if k not in afterbank[word].keys():
#                        afterbank[word][k] = 1
#                    else:
#                        afterbank[word][k] += 1
#
#            continue
#     
#        ###########################################################################
#        # if multiple lesions in the report...
#        ###########################################################################
#        for les in range(1, lesions_no + 1):
#            path_i = lesion_i_path(les, path)
#            allwords_i = allWords(path_i)
#            for k in allwords_i.keys():
#                if k not in bigbank.keys():
#                    bigbank[k] = 1
#                else:
#                    bigbank[k] += allwords_i[k]
#
#            for n_ngram in grambank.keys():
#                ngram_i = nGram(path_i, n_ngram)
#                count_k = 0
#                for k in ngram_i:
#                    if k not in grambank[n_ngram].keys():
#                        grambank[n_ngram][k] = 1
#                        continue
#                    else:
#                        count_k += 1
#                grambank[n_ngram][k] = count_k
#            
#            for word in beforebank.keys():
#                nbeforeafter_i = nBeforeAfter(path_i, word, n_beforeafter)
#                for k in nbeforeafter_i[0]:
#                    if k not in beforebank[word].keys():
#                        beforebank[word][k] = 1
#                    else:
#                        beforebank[word][k] += 1
#                    
#                for k in nbeforeafter_i[1]:
#                    if k not in afterbank[word].keys():
#                        afterbank[word][k] = 1
#                    else:
#                        afterbank[word][k] += 1
#    ###########################################################################
#    
#    # OUTPUT THE WORDBANK
#    p98 = np.percentile(list(bigbank.values()), 98)
#    filt_bigbank = {k:v for k,v in bigbank.items() if v >= p98}
#    # creat csv
#    out_bigbank = list(zip(filt_bigbank.keys(), filt_bigbank.values()))
#    out_bigbank = ps.DataFrame(out_bigbank, columns = ['word', 'count'])
#    #out_bigbank.to_csv('Feature Generating Data\\wordBank_20190820.csv')
#    
#    # OUTPUT THE NGRAM DATA
#    filt_grambank = {}
#    for ngram in grambank.keys():
#        # 99th percentile for counts
#        p99 = np.percentile(list(grambank[ngram].values()), 99)
#        # filtered dictionary
#        filt_grambank[ngram] = {k:v for k,v in grambank[ngram].items() if v >= p99}
#    # create csv
#    ngram_n_csv = []
#    ngram_k_csv = []
#    ngram_v_csv = []
#    for ngram in filt_grambank.keys():
#        ngram_n = [ngram] * len(filt_grambank[ngram])
#        ngram_n_csv = ngram_n_csv + ngram_n
#        ngram_k_csv = ngram_k_csv + list(filt_grambank[ngram].keys())
#        ngram_v_csv = ngram_v_csv + list(filt_grambank[ngram].values())
#    out_ngram = list(zip(ngram_n_csv, ngram_k_csv, ngram_v_csv))
#    out_ngram = ps.DataFrame(out_ngram, columns = ['gram', 'key', 'count'])
#    #out_ngram.to_csv("Feature Generating Data\\nGram_20190820.csv")
#
#    # OUTPUT THE BEFORE/AFTER TABLE
#    filt_beforebank = {}
#    for word in beforebank.keys():
#        # check if the value is empty
#        if beforebank[word] == {}:
#            continue
#        # 99th percentile for counts
#        p99 = np.percentile(list(beforebank[word].values()), 99)
#        # filtered dictionary
#        filt_beforebank[word] = {k:v for k,v in beforebank[word].items() if v >= p99}
#    filt_afterbank = {}
#    for word in afterbank.keys():
#        # check if the value is empty
#        if afterbank[word] == {}:
#            continue
#        # 99th percentile for counts
#        p99 = np.percentile(list(afterbank[word].values()), 99)
#        # filtered dictionary
#        filt_afterbank[word] = {k:v for k,v in afterbank[word].items() if v >= p99}
#    # create csv
#    bank_location_csv = []
#    bank_word_csv = []
#    bank_k_csv = []
#    bank_v_csv = []
#    for word in filt_beforebank.keys():
#        location_vector = ['before'] * len(filt_beforebank[word])
#        bank_location_csv = bank_location_csv + location_vector
#        word_vector = [word] * len(filt_beforebank[word])
#        bank_word_csv = bank_word_csv + word_vector
#        bank_k_csv = bank_k_csv + list(filt_beforebank[word].keys())
#        bank_v_csv = bank_v_csv + list(filt_beforebank[word].values())
#    for word in filt_afterbank.keys():
#        location_vector = ['after'] * len(filt_afterbank[word])
#        bank_location_csv = bank_location_csv + location_vector
#        word_vector = [word] * len(filt_afterbank[word])
#        bank_word_csv = bank_word_csv + word_vector
#        bank_k_csv = bank_k_csv + list(filt_afterbank[word].keys())
#        bank_v_csv = bank_v_csv + list(filt_afterbank[word].values())
#    out_beforeafter = list(zip(bank_location_csv, bank_word_csv, bank_k_csv, bank_v_csv))
#    out_beforeafter = ps.DataFrame(out_beforeafter, columns = ['location', 'keyword', 'closeword', 'count'])
#    #out_beforeafter.to_csv('Feature Generating Data\\beforeAfter_20190820.csv')  


    ###########################################################################
    ###########################################################################   
    ###########################################################################
    # Build Keywords table for sure independent sampling
    ###########################################################################
    ###########################################################################
    ###########################################################################
#    keywords = list(filt_bigbank.keys())
#    sis = []
#    index = 0
#    for r in range(0, len(data)):
#        print(r, data['Accession No'][r])
#        pathrpt = data['Report Text'][r]
#        pathrpt = pathrpt.lower().strip()
#        lesions_no = number_les_in_report(pathrpt)
#        path = path_dx_section(pathrpt)
#        if path == None:
#            path = ''
#        ###########################################################################
#        # if only one lesion in the report
#        ###########################################################################
#        if lesions_no == 1:
#            sis.append({})
#            sis[index]['Accession No'] = '{}_{}'.format(data['Accession No'][r], 1)
#            path_r = lesion_r_path(path)
#            allwords_r = list(allWords(path_r).keys())
#            for k in keywords:
#                if k in allwords_r:
#                    sis[index][k] = 1
#                else:
#                    sis[index][k] = 0
#            index += 1
#            continue
#        ###########################################################################
#        # if multiple lesions in the report...
#        ###########################################################################
#        for les in range(1, lesions_no + 1):
#            sis.append({})
#            sis[index]['Accession No'] = '{}_{}'.format(data['Accession No'][r], les)
#            path_i = lesion_i_path(les, path)
#            allwords_i = list(allWords(path_i).keys())
#            for k in keywords:
#                if k in allwords_i:
#                    sis[index][k] = 1
#                else:
#                    sis[index][k] = 0
#            index += 1
#            continue
#    csv_columns = ['Accession No'] + keywords
#    sis_matrix = ps.DataFrame(sis, columns = csv_columns)
#    #sis_matrix.to_csv("SIS_Keywords_20190821.csv")
    

#    ###########################################################################
#    ###########################################################################   
#    ###########################################################################
#    # Build +/- 5 nearby words table for sure independent sampling
#    ###########################################################################
#    ###########################################################################
#    ###########################################################################
#    # Using Ofer and I's top 30 essential keywords    
#    fn = "\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\Feature Generating Data\\SIS\\theOferList.csv"
#    csv = ps.read_csv(fn)
#    oferList= list(csv['Ofer'])
#    
#    # initialize the dictionaries
#    oferBefore = {}
#    oferAfter = {}
#    for k in oferList:
#        oferBefore[k] = {}    
#    for k in oferList:
#        oferAfter[k] = {}    
#    n_beforeafter = 5
#
#    # Establish directory and read dataline table
#    fn = "\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\DataLine Results - MED18416 - 20190710 12.09.59.xlsx"
#    xls = ps.ExcelFile(fn)
#    data = xls.parse("Results 1", skiprows=5, index_col = None)
#    
#    # filter out all but the GENERAL MEDICINE reports
#    data = data[data['Doctor Service'] == 'GENERAL MEDICINE']
#    data.reset_index(drop=True, inplace=True)
#    for r in range(0, len(data)):
#    #for r in range(0, 50):
#        #if data['Accession No'][r] == 'S18-21729': 
#        #    print(r, data['Accession No'][r])
#        print(r, data['Accession No'][r])
#        ###########################################################################
#        # identify:
#        #   number of lesions in the report
#        #   clinical dx and patient history section
#        #   pathological dx section
#        ###########################################################################
#        pathrpt = data['Report Text'][r]
#        pathrpt = pathrpt.lower().strip()
#    
#        lesions_no = number_les_in_report(pathrpt)
#        path = path_dx_section(pathrpt)
#        if path == None:
#            path = ''
#        ###########################################################################
#        # if only one lesion in the report
#        ###########################################################################
#        if lesions_no == 1:
#            path_r = lesion_r_path(path)               
#            for word in oferBefore.keys():
#                nbeforeafter_r = nBeforeAfter(path_r, word, n_beforeafter)
#                for k in nbeforeafter_r[0]:
#                    if k not in oferBefore[word].keys():
#                        oferBefore[word][k] = 1
#                    else:
#                        oferBefore[word][k] += 1
#                for k in nbeforeafter_r[1]:
#                    if k not in oferAfter[word].keys():
#                        oferAfter[word][k] = 1
#                    else:
#                        oferAfter[word][k] += 1
#            continue
#     
#        ###########################################################################
#        # if multiple lesions in the report...
#        ###########################################################################
#        for les in range(1, lesions_no + 1):
#            path_i = lesion_i_path(les, path)            
#            for word in oferBefore.keys():
#                nbeforeafter_i = nBeforeAfter(path_i, word, n_beforeafter)
#                for k in nbeforeafter_i[0]:
#                    if k not in oferBefore[word].keys():
#                        oferBefore[word][k] = 1
#                    else:
#                        oferBefore[word][k] += 1 
#                for k in nbeforeafter_i[1]:
#                    if k not in oferAfter[word].keys():
#                        oferAfter[word][k] = 1
#                    else:
#                        oferAfter[word][k] += 1
#    ###########################################################################
#    
#    # WRITE CSV OF NEARBY WORDS
#    filt_oferBefore = {}
#    for word in oferBefore.keys():
#        # check if the value is empty
#        if oferBefore[word] == {}:
#            continue
#        # 99th percentile for counts
#        p99 = np.percentile(list(oferBefore[word].values()), 99)
#        # filtered dictionary
#        filt_oferBefore[word] = {k:v for k,v in oferBefore[word].items() if v >= p99}
#    filt_oferAfter = {}
#    for word in oferAfter.keys():
#        # check if the value is empty
#        if oferAfter[word] == {}:
#            continue
#        # 99th percentile for counts
#        p99 = np.percentile(list(oferAfter[word].values()), 99)
#        # filtered dictionary
#        filt_oferAfter[word] = {k:v for k,v in oferAfter[word].items() if v >= p99}
#   
#    bank_location_csv = []
#    bank_word_csv = []
#    bank_k_csv = []
#    bank_v_csv = []
#    for word in filt_oferBefore.keys():
#        location_vector = ['before'] * len(filt_oferBefore[word])
#        bank_location_csv = bank_location_csv + location_vector
#        word_vector = [word] * len(filt_oferBefore[word])
#        bank_word_csv = bank_word_csv + word_vector
#        bank_k_csv = bank_k_csv + list(filt_oferBefore[word].keys())
#        bank_v_csv = bank_v_csv + list(filt_oferBefore[word].values())
#    for word in filt_oferAfter.keys():
#        location_vector = ['after'] * len(filt_oferAfter[word])
#        bank_location_csv = bank_location_csv + location_vector
#        word_vector = [word] * len(filt_oferAfter[word])
#        bank_word_csv = bank_word_csv + word_vector
#        bank_k_csv = bank_k_csv + list(filt_oferAfter[word].keys())
#        bank_v_csv = bank_v_csv + list(filt_oferAfter[word].values())
#    out_beforeafter = list(zip(bank_location_csv, bank_word_csv, bank_k_csv, bank_v_csv))
#    out_beforeafter = ps.DataFrame(out_beforeafter, columns = ['location', 'keyword', 'closeword', 'count'])
#    #out_beforeafter.to_csv('beforeAfter30Keywords_20190821.csv')
#    
#    
#    # WRITE MATRIX (lESION x FEATURES)
#    sis2 = []
#    #index = 0
#    for r in range(0, len(data)):
#        #if data['Accession No'][r] == 'S19-45258':
#        print(r, data['Accession No'][r])
#        pathrpt = data['Report Text'][r]
#        pathrpt = pathrpt.lower().strip()
#        lesions_no = number_les_in_report(pathrpt)
#        path = path_dx_section(pathrpt)
#        if path == None:
#            path = ''
#        ###########################################################################
#        # if only one lesion in the report
#        ###########################################################################
#        if lesions_no == 1:
#            sis2.append({})
#            sis2[-1]['Accession No'] = '{}_{}'.format(data['Accession No'][r], 1)
#            path_r = lesion_r_path(path) 
#            allwords_r = list(allWords(path_r).keys())
#            for k in oferList:
#                if k in allwords_r:
#                    sis2[-1][k] = 1
#                else:
#                    sis2[-1][k] = 0
#            for word in oferList:
#                nbeforeafter_r = nBeforeAfter(path_r, word, n_beforeafter)
#                for k in filt_oferBefore[word].keys():
#                    if k in nbeforeafter_r[0]:
#                        sis2[-1]['{}_{}_before'.format(word, k)] = 1
#                    else:
#                        sis2[-1]['{}_{}_before'.format(word, k)] = 0
#                for k in filt_oferAfter[word].keys():
#                    if k in nbeforeafter_r[1]:
#                        sis2[-1]['{}_{}_after'.format(word, k)] = 1
#                    else:
#                        sis2[-1]['{}_{}_after'.format(word, k)] = 0
#            #index += 1
#            continue
#
#        ###########################################################################
#        # if multiple lesions in the report...
#        ###########################################################################
#        for les in range(1, lesions_no + 1):
#            sis2.append({})
#            sis2[-1]['Accession No'] = '{}_{}'.format(data['Accession No'][r], les)
#            path_i = lesion_i_path(les, path)     
#            allwords_i = list(allWords(path_i).keys())
#            for k in oferList:
#                if k in allwords_i:
#                    sis2[-1][k] = 1
#                else:
#                    sis2[-1][k] = 0
#            for word in oferList:
#                nbeforeafter_i = nBeforeAfter(path_i, word, n_beforeafter)
#                for k in filt_oferBefore[word].keys():
#                    if k in nbeforeafter_i[0]:
#                        sis2[-1]['{}_{}_before'.format(word, k)] = 1
#                    else:
#                        sis2[-1]['{}_{}_before'.format(word, k)] = 0
#                for k in filt_oferAfter[word].keys():
#                    if k in nbeforeafter_i[1]:
#                        sis2[-1]['{}_{}_after'.format(word, k)] = 1
#                    else:
#                        sis2[-1]['{}_{}_after'.format(word, k)] = 0
#            #index += 1
#            continue    
#        
#    sis_matrix2 = ps.DataFrame(sis2)
#    sis_matrix2.to_csv("\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\Feature Generating Data\\SIS\\SIS_BeforeAfter30Keywords_20190823.csv")
#    
#    
    ###########################################################################
    ###########################################################################   
    ###########################################################################
    # Build nGram table for sure independent sampling
    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Using top 150 nGrams containing words in OferList each for n = 2, 3, 4
    fn = "\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\Feature Generating Data\\SIS\\theOferList.csv"
    csv = ps.read_csv(fn)
    oferList= list(csv['Ofer'])
    
    # initialize the dictionary
#    grambank = {2:{}, 3:{}, 4:{}}
    grambank = {2:{}, 3:{}}

    # Establish directory and read dataline table
    fn = "\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\DataLine Results - MED18416 - 20190710 12.09.59.xlsx"
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
        path = path_dx_section(pathrpt)
        if path == None:
            path = ''
        ###########################################################################
        # if only one lesion in the report
        ###########################################################################
        if lesions_no == 1:
            path_r = lesion_r_path(path)               
            for n_ngram in grambank.keys():
                ngram_r = nGram(path_r, n_ngram)                    
                for word in oferList:
                    for gram in ngram_r:
                        if word in gram:
                            if gram not in grambank[n_ngram].keys():
                                grambank[n_ngram][gram] = 1
                            else:
                                grambank[n_ngram][gram] += 1
            continue
     
        ###########################################################################
        # if multiple lesions in the report...
        ###########################################################################
        for les in range(1, lesions_no + 1):
            path_i = lesion_i_path(les, path) 
            for n_ngram in grambank.keys():
                ngram_i = nGram(path_i, n_ngram)                    
                for word in oferList:
                    for gram in ngram_i:
                        if word in gram:
                            if gram not in grambank[n_ngram].keys():
                                grambank[n_ngram][gram] = 1
                            else:
                                grambank[n_ngram][gram] += 1
    ###########################################################################
    
    # WRITE CSV nGrams containing keywords
    # initialize the dictionary
#    filt_grambank = {2:{}, 3:{}, 4:{}}
    filt_grambank = {2:{}, 3:{}}
    for n_ngram in grambank.keys():
        # 99th percentile for counts
        #p99 = np.percentile(list(grambank[n_ngram].values()), 99)
        # top 150 counts
        pos150 = sorted(list(grambank[n_ngram].values()), reverse = True)[149]
        # filtered dictionary
        filt_grambank[n_ngram] = {k:v for k,v in grambank[n_ngram].items() if v >= pos150}
   
    n_csv = []
    gram_csv = []
    count_csv = []
    for n_ngram in filt_grambank.keys():
        n_vector = [n_ngram] * len(filt_grambank[n_ngram])
        n_csv = n_csv + n_vector
        gram_csv = gram_csv + list(filt_grambank[n_ngram].keys())
        count_csv = count_csv + list(filt_grambank[n_ngram].values())
    out_nGram = list(zip(n_csv, gram_csv, count_csv))
    out_nGram = ps.DataFrame(out_nGram, columns = ['n', 'gram', 'count'])
    out_nGram.to_csv('Feature Generating Data\\n3Gram_Keywords_20190826.csv')
    
    
    # WRITE MATRIX (lESION x FEATURES)
    fn = "\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\Feature Generating Data\\n3Gram_Keywords_20190826.csv"
    csv = ps.read_csv(fn)
    nGram450 = ps.DataFrame(list(zip(list(csv['gram']), list(csv['n']))), columns = ['gram', 'n'])
    
    sis2 = []
    for r in range(0, len(data)):
        #if data['Accession No'][r] == 'S19-45258':
        print(r, data['Accession No'][r])
        pathrpt = data['Report Text'][r]
        pathrpt = pathrpt.lower().strip()
        lesions_no = number_les_in_report(pathrpt)
        path = path_dx_section(pathrpt)
        if path == None:
            path = ''
        ###########################################################################
        # if only one lesion in the report
        ###########################################################################
        if lesions_no == 1:
            sis2.append({})
            sis2[-1]['Accession No'] = '{}_{}'.format(data['Accession No'][r], 1)
            path_r = lesion_r_path(path)
            ngrams = []
            for n in range(2, 4):
                ngrams = ngrams + nGram(path_r, n)
            for g in range(1, len(nGram450['gram'])):
                gram = nGram450['gram'][g]
                if gram in ngrams:
                    sis2[-1][gram] = 1
                else:
                    sis2[-1][gram] = 0
            continue

        ###########################################################################
        # if multiple lesions in the report...
        ###########################################################################
        for les in range(1, lesions_no + 1):
            sis2.append({})
            sis2[-1]['Accession No'] = '{}_{}'.format(data['Accession No'][r], les)
            path_i = lesion_i_path(les, path)     
            ngrams = []
            for n in range(2, 4):
                ngrams = ngrams + nGram(path_i, n)
            for g in range(1, len(nGram450['gram'])):
                gram = nGram450['gram'][g]
                if gram in ngrams:
                    sis2[-1][gram] = 1
                else:
                    sis2[-1][gram] = 0
            continue    
        
    sis_matrix2 = ps.DataFrame(sis2)
    sis_matrix2.to_csv("\\\\pisidsderm\\Derm_Research\\Nick Kurtansky\\Path Report Dx Classification\\Feature Generating Data\\SIS\\SIS_3nGramKeywords_20190826.csv")

    


## run program
#if __name__ == "__main__":
#    main()

