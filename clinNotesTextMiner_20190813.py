########################################################################
#   Project: Long Term Followup - Ofer and Veronica
#   Title: Patient-Level Dx classification using per-lesion table and
#		Clinical notes to detect personal/family hx of melanoma
#	Author: Nick Kurtansky
#   Date: 6/27/2019
#
#   Stage 2: Per Patient Table
#   From Clinical Notes and "Per Lesion Table"   
#   Collect these variables:
#       MRN
#       Melanoma Yes/No in plt
#           Date from Path
#           Vectra #
#       BCC Yes/No in plt
#           Date from Path
#           Vectra #
#       SCC Yes/No in plt
#           Date from Path
#           Vectra #
#
#       History of melanoma Yes/No in notes
#       History of BCC Yes/No in notes
#       History of SCC Yes/No in ntes
#
#       Family Hx of melanoma from notes Yes/No
#
########################################################################


import os
import pandas as ps
import re
import csv
import numpy as np


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def fam_hx_melanoma(a_list):
    hx_no = ''
    hx_yes = ''
    
    #no_pat = re.compile('.+\s()( denies family history| negative|)( of| for|)(?: \w+)?(?: \w+)?\s(melanoma|malignant melanoma|lentigo maligna|in situ melanoma|melanoma in situ).+')    
    #yes_pat = re.compile('.+\s()( with| has| reports| diagnosed)( a|)( history|)( of| with|)(?: \w+)?(?: \w+)?\s(melanoma|malignant melanoma|lentigo maligna|in situ melanoma|melanoma in situ).+')    

    for i in a_list:
        i.lower().strip()
        i = '  {}'.format(i)

        if 'denies family history of melanoma' in i:
            hx_no = 'no'
        if 'reports history of melanoma' in i:
            hx_yes = 'yes'
            
    # if any yes => yes... elif no => no... else N/A
    if hx_yes == 'yes':
        return('yes')
    elif hx_no == 'no':
        return('no')
    else:
        return('')
    
      
def fam_hx(a_list):
    yes_pat1 = re.compile('.+\s()( with| has| reports| diagnosed)( a|)( history|)( of| with|)(?: \w+)?(?: \w+)?\s(melanoma|malignant melanoma|lentigo maligna|in situ melanoma|melanoma in situ)')    
    yes_pat2 = re.compile('.+\s()( mother| mom| father| dad| sister| brother| grandma| grandmother| grandpa| grandfather|)( with| has|)( history|)( of|)(?: \w+)?\s(melanoma|malignant melanoma|lentigo maligna|in situ melanoma|melanoma in situ)')
    
    for i in a_list:
        i.lower().strip()
        i = '  {}'.format(i)
        
        if 'reports histry of melanoma' in i:
            return('yes')
        if type(yes_pat1.match(i)) == re.Match:
            return('yes')
        if type(yes_pat2.match(i)) == re.Match:
            return('yes')
    return('')
        
    
'''
The patient denies family history of melanoma

Negative for melanoma

The patient reports history of melanoma

sister was diagnosed with ocular melanoma

Mother with history of melanoma

sister with melanoma

reports a history of ocular melanoma in his sister

father has a history multiple malignant melanomass'
'''


def prsn_hx(a_list):
    # out = [mel, bcc, scc]
    out = ['', '', '']
    
    # regex
    mel_pat_p = re.compile('.+(melanoma)')
    mel_pat_n = re.compile('.+(non-melanoma|nonmelanoma)')
    bcc_pat_p = re.compile('.+(bcc|basal cell)')
    #bcc_pat_n = re.compile('')
    scc_pat_p = re.compile('.+(scc|squamous cell)')
    #scc_pat_n = re.compile('')
    
    for i in a_list:
        i = i.lower().strip()
        i = '  {}'.format(i)
        
        if type(mel_pat_p.match(i)) == re.Match:
            out[0] = 1
            if type(mel_pat_n.match(i)) == re.Match:
                out[0] = 0
        if type(bcc_pat_p.match(i)) == re.Match:
            out[1] = 1
        if type(scc_pat_p.match(i)) == re.Match:
            out[2] = 1
    
    return out


def prsn_hx_othercancer(a_list):
    # out = [mel, bcc, scc]
    out = ['', '', '']
    
    # regex
    mel_yes_pat = re.compile('.+\s()( had| with| has| reports| diagnosed)( a|)( history|)( of| with|)(?: \w+)?(?: \w+)?\s(melanoma|malignant melanoma|lentigo maligna|in situ melanoma|melanoma in situ)')    
    bcc_yes_pat = re.compile('.+\s()( had| with| has| reports| diagnosed)( a|)( history|)( of| with|)(?: \w+)?(?: \w+)?\s(bcc|basal cell)')    
    scc_yes_pat = re.compile('.+\s()( had| with| has| reports| diagnosed)( a|)( history|)( of| with|)(?: \w+)?(?: \w+)?\s(scc|squamous cell)')    
    
    for i in a_list:
        i = i.lower().strip()
        i = '  {}'.format(i)
        
        if type(mel_yes_pat.match(i)) == re.Match:
            out[0] = 1
        if type(bcc_yes_pat.match(i)) == re.Match:
            out[1] = 1
        if type(scc_yes_pat.match(i)) == re.Match:
            out[2] = 1
    
    return out


'''
########### SKIN CANCER HISTORY
                ******* FIRST RULE ********
### Melanoma Thickness :: if anything exists => melanoma
### Melanoma Surgery Year
### Melanoma Surgery
### Melanoma Surgeon
### Melanoma Status
### Melanoma Site
### Melanoma
### Melanoma 1
### Melanoma 2
### Melanoma 3
        
### Basal Cell Carcinoma Sites :: if anything exists => bcc
### Non-Melanoma Basal Cell
        Basal cell carcinoma

### Non-Melanoma Squamous Cell :: if anything exists => scc
        Squamous cell carcinoma
        
        
### Skin cancer history melanoma
        HISTORY OF MELANOMA

### Other skin cancer history
        melanoma in situ
        atypical spitz vs. melanoma
                
### Non-melanoma skin cancer
        basal cell carcinoma
        sccis




            *** SECOND RULE ***
########### CHIEF COMPLAINT
in light of a personal history of melanoma

in light of his history of melanoma

History of melanoma
    ! NOT: FAMILY HISTORY OF MELANOMA !

history of nonmelanoma skin cancer and the melanoma on the back. The melanoma was treated in 2008

in light of her history of multiple melanomas

in light of his history of multipleborderline low-risk primary melanoma

in light of his history of an intermediate-risk primary melanoma

in light of her history of multiple, low risk, primary melanomas

opinion regarding a melanoma in situ

in light of a history of skin cancer, atypical nevi and melanoma

in light of his atypical nevi and history of an intermediate-risk primary melanoma

opinion regarding a BCC on the right forehead and two melanomas on the right  abdomen

returns for curettage and electrodessication for biopsy-proven superficial BCC





                *** THIRD RULE ***
########### INTERVAL HISTORY [INTERVAL HISTORY, Interval History:, ]
The patient is melanoma was located on the left lower leg

hx of malignant melanoma

history of MIS, atypical nevi, and basal cell carcinomas

early evolving melanoma in situ

post excision of a basal cell carcinoma

she had a BCC diagnosed

*** Any instance of BCC, SCC, or Melanoma that isn't preceeded by 
    'family history of '** Family history mother had melanoma 
    'no evidence'



########### PAST MEDICAL HISTORY
Anything BCC, SCC, Melanoma except "he/she denies family hx of..."


'''




def main():
    ###########################################################################
    ####################### Part 1 Per Lesion Table ###########################
    ###########################################################################
    
    # Establish directory and read "Part 1 Per Lesion Table"
    wd = "Z:\\3.FELLOWS_STUDENTS\\Agar Reiter Ofer\\Long term followup\\Nick's analysis"    
    os.chdir(wd)
    
    # Source: Table 1: Per Lesion
    fp_perles = 'PerLesion190813.csv'
    perlesion = ps.read_csv(fp_perles)
    perlesion.ReportDate = ps.to_datetime(perlesion.ReportDate)
    
    # Source: Clinical Notes
    xls = ps.ExcelFile('DataLine Results - MED18303 - 20190612 17.12.12.xlsx')
    notes = xls.parse("Dermatology Notes ClinDoc", skiprows=5, index_col = None)
    
    # initiate table
    mrn = []
    plt_mel = []
    plt_mel_date = []
    plt_mel_vectra = []
    plt_bcc = []
    plt_bcc_date = []
    plt_bcc_vectra = []
    plt_scc = []
    plt_scc_date = []
    plt_scc_vectra = []
    notes_hx_mel = []
    notes_hx_bcc = []
    notes_hx_scc = []
    notes_family_hx_mel = []

    study_subjects = list(set(perlesion.MRN))
    study_subjects.sort()
            
    for r in range(0, len(study_subjects)):
    #for r in range(0, 5):
           
        # patient MRN
        mrn.append(str('{:08d}'.format(study_subjects[r])))
        
        ###########################################################################
        # identify:
        #   melanoma, bcc, and/or scc dx in patholgy table
        ###########################################################################
        plt_r = perlesion[perlesion.MRN == study_subjects[r]]
        
        ##################### melanoma pathology report #####################
        if 'Melanoma' in list(plt_r['Final Classification']):
            # yes for melanoma path dx
            plt_mel.append(1) 
            
            # filter 
            plt_r_m = plt_r[plt_r['Final Classification'] == 'Melanoma']
            plt_mel_date.append(min(plt_r_m.ReportDate))      # date of first mel dx
            
            # filter
            plt_r_m = plt_r_m[plt_r_m.ReportDate == min(plt_r_m.ReportDate)]
            plt_r_m.reset_index(drop=True, inplace=True)
            plt_mel_vectra.append(plt_r_m.Vectra[0])
        else:
            plt_mel.append(0)   
            plt_mel_date.append('N/A')
            plt_mel_vectra.append('N/A')
        
        
        ##################### bcc pathology report #####################
        if 'BCC' in list(plt_r['Final Classification']):
            # yes for bcc path dx
            plt_bcc.append(1) 
            
            # filter 
            plt_r_b = plt_r[plt_r['Final Classification'] == 'BCC']
            plt_bcc_date.append(min(plt_r_b.ReportDate))      # date of first bcc dx
            
            # filter
            plt_r_b = plt_r_b[plt_r_b.ReportDate == min(plt_r_b.ReportDate)]
            plt_r_b.reset_index(drop=True, inplace=True)
            plt_bcc_vectra.append(plt_r_b.Vectra[0])
        else:
            plt_bcc.append(0)   
            plt_bcc_date.append('N/A')
            plt_bcc_vectra.append('N/A')
   
    
        ##################### scc pathology report #####################
        if 'SCC' in list(plt_r['Final Classification']):
            # yes for scc path dx
            plt_scc.append(1) 
            
            # filter 
            plt_r_s = plt_r[plt_r['Final Classification'] == 'SCC']
            plt_scc_date.append(min(plt_r_s.ReportDate))      # date of first scc dx
            
            # filter
            plt_r_s = plt_r_s[plt_r_s.ReportDate == min(plt_r_s.ReportDate)]
            plt_r_s.reset_index(drop=True, inplace=True)
            plt_scc_vectra.append(plt_r_s.Vectra[0])
        else:
            plt_scc.append(0)   
            plt_scc_date.append('N/A')
            plt_scc_vectra.append('N/A')
         
        ###########################################################################
        # identify:
        #   hx of mel, bcc, and/or scc in notes & family hx of mel in notes
        ###########################################################################
        notes_r = notes[notes.MRN == study_subjects[r]]
        
        ################# family history of melanoma ###################
        notes_r_fam = notes_r[notes_r.Section == 'FAMILY HISTORY']
        notes_r_fam1 = notes_r_fam[notes_r_fam.Item == 'Family History Melanoma']
        notes_r_fam1 = list(notes_r_fam1.Value)
        check1 = fam_hx_melanoma(notes_r_fam1)
        if check1 == 'yes':
            notes_family_hx_mel.append(check1)
        else:
            notes_r_fam2 = notes_r_fam[notes_r_fam.Item == 'Family History:']
            notes_r_fam2 = list(notes_r_fam2.Value)
            check2 = fam_hx(notes_r_fam2)
            if check2 == 'yes':
                notes_family_hx_mel.append(check2)
            elif check1 == 'no':
                notes_family_hx_mel.append('no')
            else:
                notes_family_hx_mel.append('')
        
        ################# personal history of mel, bcc, scc ###################
        notes_r_prsn = notes_r[notes_r.Section == 'SKIN CANCER HISTORY']
        notes_r_prsn_items = list(notes_r_prsn.Item)
        check1 = prsn_hx(notes_r_prsn_items)
        
        notes_r_prsn_OtherSkinCancer = notes_r_prsn[notes_r_prsn.Item == 'Other skin cancer history']
        notes_r_prsn_OtherSkinCancer = list(notes_r_prsn_OtherSkinCancer.Value)
        check2 = prsn_hx_othercancer(notes_r_prsn_OtherSkinCancer)
        
        for i in range(0,3):
            if 1 in [check1[0], check2[0]]:
                notes_hx_mel.append(1)
            else:
                notes_hx_mel.append(0)
            
            if 1 in [check1[1], check2[1]]:
                notes_hx_bcc.append(1)
            else:
                notes_hx_bcc.append(0)

            if 1 in [check1[2], check2[2]]:
                notes_hx_scc.append(1)
            else:
                notes_hx_scc.append(0)

   
    
    # column bind all lists of data into a table    
    table = list(zip(mrn, plt_mel, plt_mel_date, plt_mel_vectra, plt_bcc, \
                     plt_bcc_date, plt_bcc_vectra, plt_scc, plt_scc_date, \
                     plt_scc_vectra, notes_hx_mel, notes_hx_bcc, notes_hx_scc, notes_family_hx_mel))
    output = ps.DataFrame(table, columns = ['MRN', 'mel_path', 'mel_path_d', \
                                            'mel_path_v', 'bcc_path', 'bcc_path_d', \
                                            'bcc_path_v', 'scc_path', 'scc_path_d', \
                                            'scc_path_v', 'mel_note', 'bcc_note', 'scc_note', 'fam_mel_note'])
    output.to_csv("PerPatient_20190813.csv")


# run program
if __name__ == "__main__":
    main()

