"""
Author: Nicholas Kurtansky
Date Initiated: 6/24/2019
Title: Change image filenames and move to patientlevel folders: studyID_VectraID_#

Using a VectraQuery csv output as the data dictionary, copy image files into 
patient folders.
Output a new table preserving MRN and Study ID.
   
Last update
    Date: 
    Summary: 
"""


import shutil
import os
import pandas
import numpy


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Takes a general character string and returns the 
# indexes in a folder containing that string in the filename
def get_exact_names_index(string, path):
    # error checking - in case there is no such folder in the database
    try:
        #string = string.lower()
        in_folder = os.listdir(path)
        indexes = []
        for i in in_folder:
            if string == i:#.lower():
                # append to list of indexes if file contains the string
                indexes.append(in_folder.index(i))
        return indexes
    except (FileNotFoundError):
        pass


# Takes a general character string and returns the 
# indexes in a folder containing that string in the filename
def get_similar_names_index(string, path):
    # error checking - in case there is no such folder in the database
    try:
        string = string.lower()
        in_folder = os.listdir(path)
        indexes = []
        for i in in_folder:
            if string in i.lower():
                # append to list of indexes if file contains the string
                indexes.append(in_folder.index(i))
        return indexes
    except (FileNotFoundError):
        pass


# Takes list of indexes of a folder and copies indexed files
# to a local temporary directory.
# Then moves the files under a new file name to the flat flder
# Finally, deletes the temporary directory.
# ALSO returns path of the first image copied as well as the number
# of images copied - info to be used in an outputted file mapping table
def copy_similar_images(old_path, indexes, new_path, string_name = ""):
    # error checking = in case there is no such folder in the database
    try:
        # list contents of the existing folder
        in_old_folder = os.listdir(old_path)
        
        # create a temporary working directory where files can be copied,
        # renamed, and finally moved.
        # necessary in order to preserve original files and metadata using shutil.copy2()
        # necessary because file names cannot be changed as they pass through shutil.copy2()
        os.mkdir("Temp")            # This could really slow the program down...
        temp = "Temp"
        
        # initiate count which is used for file names and reported back in the return
        count = 1
        new_name=""
        out_name=""
        name_and_count = []
        for i in indexes:
            # existing file name to be passed into shutil.copy2()
            old_file = old_path + "\\" + in_old_folder[i]
            shutil.copy2(src = old_file, dst = temp)
            
            # with file in temporary location, we change name and move to flat file
            new_name = new_path + "\\" + string_name + "_" + str(count) + ".jpg"        
            os.rename(src = temp + "\\" + in_old_folder[i], dst = new_name)
            
            # list only first file copied in the return
            if count == 1:
                out_name = new_name
            count += 1
        
        # delete temporary working directory and return 1st fname and # of images
        shutil.rmtree("Temp")
        name_and_count.append(out_name)
        name_and_count.append(count-1)
        return(name_and_count)
        
    except (FileNotFoundError):
        return(["", 0])


# Copies a file to a local temporary directory.
# Then moves the file under a new file name to the flat flder
# Finally, deletes the temporary directory.
# ALSO returns image path
def copy_images(old_path, new_path, string_name = ""):
    # error checking = in case there is no such folder in the database
    try:
       
        # create a temporary working directory where files can be copied,
        # renamed, and finally moved.
        # necessary in order to preserve original files and metadata using shutil.copy2()
        # necessary because file names cannot be changed as they pass through shutil.copy2()
        os.mkdir("Temp")   # This could really slow the program down...
        temp = "Temp"
        
        # initiate count which is used for file names and reported back in the return
        new_name=""

        # existing file name to be passed into shutil.copy2()
        shutil.copy2(src = old_path, dst = temp)
        
        # with file in temporary location, we change name and move to flat file
        temp_name = temp + "\\" + old_path.split("\\")[-1]
        new_name = new_path #+ "\\" + string_name     
        os.rename(src = temp_name, dst = new_name)
        
        # delete temporary working directory and return 1st fname and # of images
        shutil.rmtree("Temp")
        return(new_name)
        
    except (FileNotFoundError):
        return([""])


def main():

    # user will input these in the finished product. For efficiency in development, let them already be specified """
    time_stamp = "20190718"
        #   Establish working directory
    #wd = "\\pisidsderm\Derm_Research\3.FELLOWS_STUDENTS\Agar Reiter Ofer\Melanoma associated with nevus\MelArisingInNevusWithVectra"
    wd = 'Z:\\3.FELLOWS_STUDENTS\Agar Reiter Ofer\\Melanoma associated with nevus\\MelArisingInNevusWithVectra'
    os.chdir(wd)
        #   Read csv table into a dataframe using pandas
    csv_name = pandas.read_csv("MirrorExportUtility.csv", delimiter = ",")
    csv_name['link'] = ''
        #   User input the column index of the ImagePath
    lesion_col = 5
    mrn_col = 4
    date_col = 1
        #   Enter name of the old folder containing many folders of images
    old_folder = "{}\\MarghoobImages".format(wd)
            #   Enter name of folder to be created
    new_folder = "{}\\MarghoobImages_{}".format(wd, time_stamp)
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)
    
    # initialize fields needed for file mapping table
    path_list = []
    
    # add leading zeroes to mrn
    csv_name.MRN = csv_name.MRN.astype(str)
#    for i in range(len(csv_name.IMAGEID)):
#        mrn = int(csv_name.MRN[i])
#        csv_name.MRN[i] = '{:08d}'.format(mrn)

    # for matching filenames
    csv_name.IMAGEID = csv_name.IMAGEID.astype('str')
#    for i in range(len(csv_name.IMAGEID)):
#        csv_name.IMAGEID[i] = str(csv_name.IMAGEID[i][0:17])

    # initiate patient dictionary for counting
    patient_set = set(csv_name.iloc[:, mrn_col])
    patient_dict = dict.fromkeys(patient_set, 0)
    
    # create individual patient folders
    for pat in patient_set:
        os.mkdir("{}\\{}".format(new_folder, pat))

    
    # to monitor progress of the program while running
    images_to_move = len(csv_name.IMAGEID)
    images_moved = 0     
    
    # loop though all images in old flat folder
    for fn in os.listdir(old_folder):
        
        # split filename
        fn_im = fn.split(" ")
        fn_im = fn_im[-1]
        fn_im = fn_im[:fn_im.find(".")]
        try:
            fn_im = int(fn_im)#[0:-2])
            fn_im = str(fn_im)
            
            # find row in the csv
            csv_id = numpy.where(csv_name.IMAGEID == fn_im)
            csv_id = list(csv_id[0])[0]
                        
            # pull info for fn
            mrn_i = csv_name.iloc[csv_id, mrn_col]
            date_i = csv_name.iloc[csv_id, date_col][0:10]
            count_i = patient_dict[mrn_i]
            patient_dict[mrn_i] = count_i + 1
            lesion_i = csv_name.iloc[csv_id, lesion_col]
            
            # new filename and folder
            filename = "les{}_{}_n{}.jpg".format(lesion_i, date_i, count_i)
            folder = "{}\\{}".format(new_folder, mrn_i)
            new_path = "{}\\{}".format(folder, filename)
            
            # old fn
            old_path = "{}\\{}".format(old_folder, fn)
            
            # move images
            path_and_count = copy_images(old_path, new_path, string_name = "")
            path_list.append(path_and_count)
        
            # add filepath to table
            csv_name['link'][csv_id] = path_and_count
                        
            # monitor progress
            images_moved += 1
            print('{}%.....{}'.format(round(images_moved / images_to_move * 100, 2), fn_im))
            
        except(ValueError):
            #path_list.append("Error")
            print(fn_im + " ~~~ ERROR ~~~")
   
    # create the new file mapping table
    out = csv_name
    
    # cast to type string
    out.IMAGEID = out.IMAGEID.astype('str')
    out.MRN = out.MRN.astype('str')

    out.to_csv("Ofer_FileList_" + time_stamp +".csv")
    

# run program
if __name__ == "__main__":
    main()