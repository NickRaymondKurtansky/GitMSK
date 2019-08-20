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


def main():
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
    out_beforeafter.to_csv('beforeAfter_20190820.csv')


## run program
#if __name__ == "__main__":
#    main()

