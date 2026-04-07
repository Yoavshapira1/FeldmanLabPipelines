
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 16:39:48 2019

@author: Tolik
"""


import mne
import os
import pandas as pd


outFolderName = 'output folder'
inFolderPath = 'source folder with EEG files'
excelName = "table with start and end time of each interaction.xlsx"

# prep part
os.chdir(inFolderPath)  # script dir is work dir
log_file = open(outFolderName+"log_file.txt", "w+")  # LOG
if not os.path.exists(outFolderName):
    os.makedirs(outFolderName)
xl_sheet_names = pd.ExcelFile(excelName).sheet_names
file_ext_ls = []
log_file.write(">>> SHEETS IN XL FILE:\n "+",\n".join(xl_sheet_names)+"\n\n")  # LOG
#log_file.write("BO_clean\n "+",\n".join(xl_sheet_names)+"\n\n")  # LOG


for sheet in xl_sheet_names:
    dic = {}
    log_file.write(">>> WORKING ON SHEET:\n"+sheet+"\n\n")  # LOG
    target_fd = outFolderName+sheet
    if not os.path.exists(target_fd):
        os.makedirs(target_fd)
    df = pd.read_excel(excelName, sheet_name = sheet)
    filename = df["file"].values
    t1 = df["t1"].values
    t2 = df["t2"].values
    log_file.write(">>> SUBJECT NAME AND TIME TRIPLETS:\n")
    for i in range(len(filename)):
        log_file.write("SUBJECT:   {: <12} T1: {: <10} T2: {}\n"\
                       .format(filename[i], str(t1[i]), str(t2[i])))
    log_file.write("\n>>> CROPPING SUBJECTS (PASSED TIME TO CROP FUNCTION):\n")
    for i,file in enumerate(filename):
        
        if 'nan' in [str(file), str(t1[i]), str(t2[i])] or\
            (not os.path.isfile(file+".vhdr")):
           continue
        file_ext = file[0:11]
        #load and crop subject in current itteration
        raw = mne.io.read_raw_brainvision(file+".vhdr", preload = True)
        subject = raw.copy()
        t_start = int(t1[i])/1000
        t_end = int(t2[i])/1000
        subject = subject.crop(t_start, t_end)
        log_file.write("CROPPING SUBJECT:  {: <12} at starting time: {: <10} finish time: {: <10}, ".format(str(file), t_start, t_end))  # LOG
        
        #if we need to append to existing file (from previous itteration)
        if file_ext+sheet in file_ext_ls:
            log_file.write("CONCATENATING\n".format(file))  # LOG
            #renaming the existing file in order to avoid name error when 
            #saving again to the same name ('overwrite = True' didn't help)
            os.rename(outFolderName+sheet+'/'+file_ext+sheet+'_raw.fif',
                      outFolderName+sheet+'/'+'temp2'+'_raw.fif')
            #save the current vhdr as fif, so it can be reloaded
            #solves a raw type confliction that happens otherwise
            subject.save('temp_raw.fif',overwrite=True)
            raw = mne.io.read_raw_fif('temp_raw.fif')
            subject_acc = mne.io.read_raw_fif(outFolderName+sheet+'/'+
                                              'temp2'+'_raw.fif')
            #concat the current and accumulated file
            subject_new = mne.io.concatenate_raws([raw, subject_acc])
            newfile1= file_ext+sheet+'_raw.fif' 
            newfile1 = os.path.join(target_fd, newfile1)
            subject_new.save(newfile1, overwrite=True)
            duration = int(len(subject_new)/1000)
            dic[file] = duration
            
            raw = None
            subject_new = None
            os.remove(outFolderName+sheet+'/'+'temp2'+'_raw.fif')
            os.remove('temp_raw.fif')
#            
            pass
        #generate a new file
        else:
            log_file.write("GENERATING NEW FILE\n".format(file))  # LOG
            newfile1= file_ext+sheet+'_raw.fif'
            newfile1 = os.path.join(target_fd, newfile1)
            subject.save(newfile1,overwrite=True)
            file_ext_ls.append(file_ext+sheet)    
            duration = int(len(subject)/1000)
            dic[file] = duration
    log_file.write("\n")
    
    print(">>> DURATION OF CROPPED RAW FILE (IN SECONDS):")
    for key, val in dic.items():
        log_file.write("SUBJECT: {: <12}, DURATION: {: <10}\n".format(key, val))
    log_file.write("\n")
            
log_file.close()