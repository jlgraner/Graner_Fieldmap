#This script will create a fieldmap using FSL. It is specific to the format we're getting out of BIAC.
#It is also written to work, not to be pretty. There are more elegant ways to do this stuff, but
#this will work for now.

#Steps:
#   1) Pull out magnitude image for short TE and magnitude image for long TE (3dTcat)
#   2) Pull out real and imaginary images for short and long TE (3dTcat)
#   2) Extract brain from magnitude images using (BET)
#   3) Register long-TE magnitude image to short-TE magnitude image using (FLIRT)
#   4) Apply registration matrix to long-TE real and imaginary images (FLIRT)
#   5) Compile real and imaginary images into a single complex image for each TE (FSLCOMPLEX)
#   6) Create unwrapped phase images for long and short TEs (PRELUDE)
#   7) Subtract unwrapped phase images to create fieldmap (FSLMATHS)
#   8) Smooth and despike fieldmap (FUGUE)

##Author: John Graner, Ph.D., LaBar Lab, Center for Cognitive Neuroscience, Duke University, Durham, NC

import os

#---------CHANGE THESE THINGS--------------------
subject_id = '21906'        #BIAC exam number
b0_scan_id = '005'          #BIAC scan ID of the B0 fieldmap acquisition
biac_scanner_number = '5'   #e.g. 5 or 6
te_short = '0.007'          #Only change these if you altered the TEs used in the acquisition.
te_long = '0.009'
#Make this the directory containing each subject directory
base_b0_dir = '/your/study/Data/{}'.format(subject_id)

smoothing = '6.0'
delete_existing = True      #Set to True to delete any pre-existing output, set to False to stop instead
#-------------------------------------------------

te_dif = float(te_long) - float(te_short)

#Make sure everything is there
print('Checking to make sure everything we need is here...')
if not os.path.exists(base_b0_dir):
    print('base_b0_dir cannot be found: {}'.format(base_b0_dir))
    print('Double-check that it exists!')
    raise OSError
else:
    print('Base b0 directory found...')
    
mag_file_both = os.path.join(base_b0_dir, 'bia{}_{}_{}_1-1.nii.gz'.format(biac_scanner_number, subject_id, b0_scan_id))
real_file_both = os.path.join(base_b0_dir, 'bia{}_{}_{}_2-2.nii.gz'.format(biac_scanner_number, subject_id, b0_scan_id))
imag_file_both = os.path.join(base_b0_dir, 'bia{}_{}_{}_3-3.nii.gz'.format(biac_scanner_number, subject_id, b0_scan_id))

for element in [mag_file_both, real_file_both, imag_file_both]:
    if not os.path.exists(element):
        print('Image file could not be found: {}'.format(element))
        raise OSError
print('B0 image files found...')

#Create output directory if needed
output_dir = os.path.join(base_b0_dir, 'fieldmap_{}'.format(b0_scan_id))
if not os.path.exists(output_dir):
    print('Creating output directory: {}'.format(output_dir))
    os.mkdir(output_dir)
else:
    if not delete_existing:
        print('Output directory already exists and delete_existing is not set to True!')
        print('Exitting so as not to inadvertently erase existing data!')
        raise OSError
    else:
        print('Output directory already exists and delete_existing is set to True.')
        print('Deleting existing output...')
        for element in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, element))


#Pull out magnitude images
print('Isolating magnitude images...')
mag_short_image = os.path.join(output_dir, 'mag_short.nii')
mag_long_image = os.path.join(output_dir, 'mag_long.nii')
command = "3dTcat -prefix {} {}'[0]'".format(mag_short_image, mag_file_both)
os.system(command)
command = "3dTcat -prefix {} {}'[1]'".format(mag_long_image, mag_file_both)
os.system(command)
print('Brain-extracting magnitude images...')
mag_short_brain_image = os.path.join(output_dir, 'mag_short_brain.nii.gz')
mag_long_brain_image = os.path.join(output_dir, 'mag_long_brain.nii.gz')
command = "bet {} {} -f 0.5 -g 0".format(mag_short_image, mag_short_brain_image)
os.system(command)
command = "bet {} {} -f 0.5 -g 0".format(mag_long_image, mag_long_brain_image)
os.system(command)

#Separate the compound images into real and imaginary
print('Separting out real and imaginary parts...')
real_short_image = os.path.join(output_dir, 'real_short.nii')
imag_short_image = os.path.join(output_dir, 'imag_short.nii')
real_long_image = os.path.join(output_dir, 'real_long.nii')
imag_long_image = os.path.join(output_dir, 'imag_long.nii')
command = "3dTcat -prefix {} {}'[0]'".format(real_short_image, real_file_both)
os.system(command)
command = "3dTcat -prefix {} {}'[0]'".format(imag_short_image, imag_file_both)
os.system(command)
command = "3dTcat -prefix {} {}'[1]'".format(real_long_image, real_file_both)
os.system(command)
command = "3dTcat -prefix {} {}'[1]'".format(imag_long_image, imag_file_both)
os.system(command)

#Register the long TE images to the short TE images
print('Registering long TE images to short TE images...')
real_long_reg_image = os.path.join(output_dir, 'real_long_reg.nii.gz')
imag_long_reg_image = os.path.join(output_dir, 'imag_long_reg.nii.gz')
mag_long_brain_reg_image = os.path.join(output_dir, 'mag_long_brain_reg.nii.gz')
reg_mat = os.path.join(output_dir, 'long_to_short.mat')
command = "flirt -in {} -ref {} -out {} -omat {}".format(mag_long_brain_image, mag_short_brain_image, mag_long_brain_reg_image, reg_mat)
os.system(command)
command = "flirt -in {} -ref {} -out {} -applyxfm -init {}".format(real_long_image, mag_short_brain_image, real_long_reg_image, reg_mat)
os.system(command)
command = "flirt -in {} -ref {} -out {} -applyxfm -init {}".format(imag_long_image, mag_short_brain_image, imag_long_reg_image, reg_mat)
os.system(command)

#Create complex images to read into prelude
print('Creating complex images...')
complex_short_image = os.path.join(output_dir, 'complex_short.nii.gz')
complex_long_image = os.path.join(output_dir, 'complex_long.nii.gz')
command = "fslcomplex -complex {} {} {}".format(real_short_image, imag_short_image, complex_short_image)
os.system(command)
command = "fslcomplex -complex {} {} {}".format(real_long_reg_image, imag_long_reg_image, complex_long_image)
os.system(command)

#Call prelude to write unwrapped phase images
print('Unwrapping phases...')
uphase_short_image = os.path.join(output_dir, 'uphase_short.nii')
uphase_long_image = os.path.join(output_dir, 'uphase_long.nii')
command = "prelude -c {} -o {} --removeramps -f -v -m {}".format(complex_short_image, uphase_short_image, mag_short_brain_image)
os.system(command)
command = "prelude -c {} -o {} --removeramps -f -v -m {}".format(complex_long_image, uphase_long_image, mag_short_brain_image)
os.system(command)

#Create the fieldmap from the unwrapped phase images
print('Creating fieldmap...')
fieldmap_image = os.path.join(output_dir, 'fieldmap_{}.nii.gz'.format(b0_scan_id))
command = "fslmaths {} -sub {} -div {} {} -odt float".format(uphase_long_image, uphase_short_image, str(te_dif), fieldmap_image)
os.system(command)

#Smooth and despike the fieldmap
print('Despiking and smoothing fieldmap...')
fieldmap_processed_image = os.path.join(output_dir, 'fieldmap_{}_final.nii.gz'.format(b0_scan_id))
command = "fugue --loadfmap={} -s {} --savefmap={}".format(fieldmap_image, smoothing, fieldmap_processed_image)
os.system(command)
