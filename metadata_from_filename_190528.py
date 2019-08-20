"""
Author: Nicholas Kurtansky
Date Initiated: 5/23/2019
Subject: Pull metadata out of filename - Natalia Jaimes dataset

functions:
    get_sex(filename):
    get_age(filename):
    get_anatomic_site(filename):
    get_diagnosis(filename):
    main():

Last update
    Date: 190528
    Summary: Manually edited files with a __ (2*_) divider to split on.
    Manually edited files with "." to "pt" so they can be opened with hyperlink.
    I will edit the functions so that they understand this standardization
    in order to more accurately pull metadata out of filenames.
    
    Return None rather than "null" if unable to parse metadata for a field
"""


import os
import pandas


# try to detect sex from image filename
def get_sex(filename, folder_splitter, fn_splitter):
    # add to this set of keywords as you encounter ways they are referenced
    keywords = set(["female", "f", "woman",
                    "male", "m", "man"])
       
    # split the distinct folders of the filepath
    filesplit = filename.split(folder_splitter)

    # loop through each folder component searching for sex identifiers      
    for f in range(len(filesplit)-1, -1, -1):
        # clean up f
        f_cln = filesplit[f].replace(" ", "")
        f_cln = f_cln.replace(",", "")
        f_cln = f_cln.lower()
        f_cln = f_cln.replace(".jpg", "")
        
        # split it at each #
        fsplit = f_cln.split(fn_splitter)
                                   
        # scan list of special words
        for j in range(len(fsplit)):
            if fsplit[j] in keywords:
                # if a keyword is detected, pull from the original filename
                f_out = filesplit[f].split(fn_splitter)
                return(f_out[j].replace(".jpg", "").replace(".JPG", "").replace("NEF", ""))
                
    # return null value if nothing is found
    return(None)
                
            

# try to detect age from filename
def get_age(filename, folder_splitter, fn_splitter):
    # add to this set of keywords as you encounter ways they are referenced
    keywords = ["yo", "yearsold", "years"]
    
    # split the distinct folders of the filepath
    filesplit = filename.split(folder_splitter)

    # loop through each folder component searching for sex identifiers      
    for f in range(len(filesplit)-1, -1, -1):
        # clean up f
        f_cln = filesplit[f].replace(" ", "")
        f_cln = f_cln.replace(",", "")
        f_cln = f_cln.lower()
        
        # split it at each #
        fsplit = f_cln.split(fn_splitter)
                                   
        # scan list of special words
        for j in range(len(fsplit)):
            for k in range(len(keywords)):
                if keywords[k] in fsplit[j]:
                    spotindex = fsplit[j].find(keywords[k])   
                    # if a keyword is detected, pull the two digits                                        
                    return(fsplit[j][spotindex-2:spotindex])
    # return null value if nothing is found
    return(None)


# try to detect anotomic site from filename
def get_anatomic_site(filename, folder_splitter, fn_splitter):
    # add to this set of keywords as you encounter ways they are referenced
    keywords = ["cheek", "forearm", "upperback", "buttock", "neck", "shoulder",
                       "thigh", "abdomen", "chest", "sole", "heel", 
                       "groin", "helix", "ear", "earlobule", "scalp", "upperabdomen",
                       "uppercheek", "rightuperback", "posteriorscalp", "breast", 
                       "forehead", "face", "leg", "axillae", "nose", "lowerback",
                       "oral", "genital", "back", "arm", "facial"]
    
    # split the distinct folders of the filepath
    filesplit = filename.split(folder_splitter)

    # loop through each folder component searching for anatomic identifiers      
    for f in range(len(filesplit)-1, -1, -1):
        # clean up f
        f_cln = filesplit[f].replace(" ", "")
        f_cln = f_cln.replace(",", "")
        f_cln = f_cln.lower()
        
        # split it at each #
        fsplit = f_cln.split(fn_splitter)
                                   
        # scan list of special words
        for j in range(len(fsplit)):
            for k in range(len(keywords)):
                if keywords[k] in fsplit[j]:
                    # if a keyword is detected, pull from the original filename
                    f_out = filesplit[f].split(fn_splitter)
                    return(f_out[j].replace(".jpg", "").replace(".JPG", "").replace("NEF", ""))
                
    # return null value if nothing is found
    return(None)


# try to detect diagnosis from filename
def get_diagnosis(filename, folder_splitter, fn_splitter):
    # add to this set of keywords as you encounter ways they are referenced
    keywords = ["spitznevus", "nevi", "ak", "bcc", "caa", "df", "sk", "lplk",
                     "sccis", "scc", "sebaceoushyperplasias", "cmn", "envus",
                     "lentigo", "actinickeratosis", "adnexaltumor", "aimp", 
                     "cutaneousmets", "cca",
                     "angiokeratoma", "angioma", "basalcellcarcinoma", "cafeaulaitmacule",
                     "dermatofibroma", "ephelis", "lentigonos", "lentigosimplex", 
                     "melanomametastasis", "melanoma", "merkelcellcarcinoma",
                     "mucosalmelanosis", "nevusspilus", "epidermalnevus", "nevus", 
                     "seborrheickeratosis",
                     "solarlentigo", "squamouscellcarcinoma", "clearcellacanthoma",
                     "atypicalspitztumor", "acrochordon", "angiofibroma", 
                     "fibrouspapule", "neurofibroma", "pyogenicgranuloma", 
                     "scar", "sebaceousadenoma", "verruca", "atypicalmelanocyticproliferation",
                     "pigmentedbenignkeratosis", "vascularlesion", "other"]

    # split the distinct folders of the filepath
    filesplit = filename.split(folder_splitter)

    # loop through each folder component searching for anatomic identifiers      
    for f in range(len(filesplit)-1, -1, -1):
        # clean up f
        f_cln = filesplit[f].replace(" ", "")
        f_cln = f_cln.replace(",", "")
        f_cln = f_cln.lower()
        
        # split it at each #
        fsplit = f_cln.split(fn_splitter)
                                   
        # scan list of special words
        for j in range(len(fsplit)):
            for k in range(len(keywords)):
                if keywords[k] in fsplit[j]:
                    # if a keyword is detected, pull from the original filename
                    f_out = filesplit[f].split(fn_splitter)                                    
                    return(f_out[j].replace(".jpg", "").replace(".JPG", "").replace("NEF", ""))
                
    # return null value if nothing is found
    return(None)


def main():
    # let's get a timestamp for the output filename
    timestamp = input("Enter today's date (yymmdd): ")
    #output_location = input("Enter and output location for your excel file: ")
    output_location = "Z:\\Nick Kurtansky\\Natalia dataset"
    
    # let's change the working directory
    wd = "Z:\\Nick Kurtansky\\Natalia dataset\\Images for ISIC\\Natalia Jaimes"
    os.chdir(wd)
    
    # walk function to get all .jpg files in the directory 
    images_long = []
    for root, dirs, files in os.walk(wd):
        for file in files:
            if file.lower().endswith(".jpg") or file.lower().endswith(".nef"):
                images_long = images_long + [os.path.join(root, file)]
    
    # let's cut out the fat
    redundant = "{}\\".format(wd)
    images = [i.replace(redundant, "") for i in images_long]
    
    # initialize the vectors which will become our excel columns
    subfolder = []
    paths = []
    age = []
    sex = []
    anatomic = []
    diagnosis = []
    
    # loop through all image files
    for img in images:
        # ._ files are created automatically by Mac OS X and contain metadata 
        # related to the accompanying file that was placed there by programs 
        # in the Mac. In order to prevent confusion, such files should not 
        # be included in the Excel file.
        if "._" in img:
            continue
        subfolder.append(img[:img.find("\\")])
        paths.append("{}\\{}".format(wd, img))
        age.append(get_age(img, "\\", "__"))
        sex.append(get_sex(img, "\\", "__"))
        anatomic.append(get_anatomic_site(img, "\\", "__"))
        diagnosis.append(get_diagnosis(img, "\\", "__"))
    
    # create the excel table
    d = {"subfolder":subfolder, "filepath":paths, "age":age, "sex":sex, "anatomic site":anatomic, "diagnosis":diagnosis}
    
    out = pandas.DataFrame(data = d)
    os.chdir(output_location)
    out.to_csv("FileList_" + timestamp +".csv")

    
# run program
if __name__ == "__main__":
    main()