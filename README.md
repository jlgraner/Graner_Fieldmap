# Graner_Fieldmap

## Intro:
This repository is meant to contain tools for use in creating and/or using B0 fieldmaps for EPI data.

## make_fieldmap_graner.py
### Summary:
This script is meant to create a fieldmap from data collected using the "ncanda-grefieldmap-v1" acquisition at BIAC.

### Dependencies:
This script requires python (2.7x or above), FSL, and AFNI to be installed. In the future it may only require python and FSL.

### Usage:
You’ll first need to move the three fieldmap Nifti files (the ones that share a common BIAC 3-digit acquisition number) into a common directory. In this script, this directory is stored in the “base_b0_dir” variable. The script will create a subdirectory in this directory called “fieldmap_###”, where ### is the number of the b0 acquisition (e.g. 005). Output from the script will be written to this new directory.

To use the script, first make a copy of it somewhere you can run it with python. Open the copy in a basic text editor (Textedit, Notepad++, Wordpad, etc.), make any necessary changes to the values in the “CHANGE THESE THINGS” section at the top of the script, and save it. You will almost certainly need to change “subject_id”, “b0_scan_id”, and “base_b0_dir”.

Once these have been changed, open up a Terminal (Mac) or Command Prompt (Windows) window, navigate to the directory containing make_fieldmap_graner.py (unless you’ve added it to your system path already), type “python -m make_fieldmap_graner”, and hit Enter. The script should take on the order of a minute to finish.

### Putting the Results Into FSL:
FSL needs the following to do B0 inhomogeneity correction…  
**Fieldmap:** the “fieldmap_NUM_final.nii.gz” file created by make_fieldmap_graner.py  
**Fieldmap mag:** the “mag_short_brain.nii.gz” file created by make_fieldmap_graner.py  
**Effective EPI echo spacing:** this is reported as “echospacing” in the fMRI you want to correct (NOT THE FIELDMAP) .bxh file. It seems to be reported in secE-6, so a value of “468” in the .bxh would be entered as “0.468” in the FSL GUI.  
**EPI TE:** this is just the TE of the fMRI (AGAIN, NOT THE FIELDMAP), which is also reported in the .bxh file as, appropriately, “te”. This value looks to be reported in ms in the .bxh file.  
**Unwarp direction:** This will potentially vary from EPI sequence to EPI sequence. Try “y” first. If that causes the resulting corrected image to look MORE warped, try “-y”.

### Looking at the Effects of Correction:
FSL outputs a pictures to roughly evaluate the effects of the b0 correction. In the report html file, click on “Registration” and then on “Unwarp”. Ideally, the unwarped EPI data better match the shape of the anatomical image, particularly in the prefrontal cortex and occipital cortex. If the unwarped EPI data look worse, try reversing the sign of the **Unwarp direction:** in the GUI.
