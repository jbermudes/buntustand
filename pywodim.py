#!/usr/bin/env python

#******************************************************************************
#	PyWodim - Python wodim Module
#
#	Copyright (C) 2008 Jess Bermudes
#	License GPLv2+: GNU GPL version 2 or later <http://gnu.org/licenses/gpl.html>
#	This is free software: you are free to change and redistribute it.
#	There is NO WARRANTY, to the extend permitted by law.
#
#
#	Author: Jess Bermudes
#	Email: jbermudes@gmail.com
#	Last Updated: December 22, 2008
#
#	Pywodim is a Python module for burning an ISO file to disc using wodim
#	Most of the heavy lifting is done by the following linux programs:
#	
#	wodim   - does the actual burning
#	md5sum  - verifies data integrity
#	mount   - checks for disc mount
#	eject   - opens/closes drive tray
#	volname - gets the disc's volume name
#	mount	- for testing the status of a device mount
#	grep	- for determining certain output results
#
#	PyWodim also makes extensive use of the Linux CD-ROM
#	standard as described in /usr/include/linux/cdrom.h
#	in order to talk to the drive and query its status
#	via ioctl commands.
#
#******************************************************************************


# python's magical imports
import sys
import string
import os
import time
import fcntl
from string import *
from subprocess import *

__version__ = 0.1

# Linux CD-ROM Standard IOCTL commands
IOCTL_CDROM_EJECT 			= 0x5309
IOCTL_CDROM_CLOSETRAY 		= 0x5319
IOCTL_CDROM_DRIVE_STATUS 	= 0x5326
IOCTL_CDROM_DISC_STATUS 	= 0x5327
IOCTL_CDROM_MEDIA_CHANGED	= 0x5325

# Responses to ioctl DRIVE_STATUS and DISC_STATUS
# NOTE: DISC_STATUS can also return NO_[INFO|DISC]
CD_STATUS =	{'NO_INFO' : 0, # if returned by drive: unable to get status
							# if returned by disc: no data

			'NO_DISC' : 1, # no disc inserted
			'TRAY_OPEN' : 2, # tray is open
			'DRIVE_NOT_READY' : 3, # drive not ready
			'DISC_OK' : 4, # disc has been inserted, no guarantee on contents
			'AUDIO' : 100, # disc is formaated for audio data
			'DATA_1' : 101, # disc is formatted for data (this is the usual case)
			'DATA_2' : 102, # disc is formatted for data (have not tested extensively)
			'XA_2_1' : 103, # disc is formatted in eXtended Architecture
			'XA_2_2' : 104, # disc is formatted in eXtended Architecture
			'MIXED' : 105 }	# disc is formatted for mixed data

# based on the numbers above, if a cd has data on it (!blank | !bad) 
# then it's return code should be greater than this number
USED_CD_STATUS_MIN = 100 

# 
CD_MEDIA_PRESENT = 0
CD_MEDIA_ABSENT = 1

# from testing, a blank cd will set the drive status to DISC_OK
# but the disc status will be NO_INFO
BLANK_CD_STATUS = CD_STATUS['DISC_OK'] | CD_STATUS['NO_INFO']

# linux program cmd strings
TRAY_OPEN_CMD 	= "eject "
TRAY_CLOSE_CMD 	= "eject -t "

WODIM_DEVICE_SCAN_CMD = "wodim --devices"
WODIM_BURN_CMD = "wodim"

VOLNAME_CMD = "volname "


# arg strings
WODIM_DEV_ARG		= " dev="
WODIM_DUMMY_ARG 	= " --dummy"
WODIM_VERBOSE_ARG 	= " -v"
WODIM_SPEED_ARG		= " speed="
WODIM_EJECT_ARG		= " -eject"

# wodim exit codes
WODIM_EXIT_CODE_SUCCESS = 0

# default devices
DEV_CDR_DEFAULT = "/dev/cdr"
DEV_CDRW_DEFAULT = "/dev/cdrw"
DEV_CDROM_DEFAULT = "/dev/cdrom"

# default directories
DIR_CDROM_DEFAULT = "/cdrom"

# *****************************************************************************

def getDefaultDevice():
	"""searches the system for a CD burning device
	
	Devices are searched for in the following order:
	CDRW, CDR
	
	Returns:
	a string of the path to a valid CD burning device, None if no suitable devices found.
	"""
	
	device = None
	if os.path.exists(DEV_CDRW_DEFAULT) is True:
		device =  DEV_CDRW_DEFAULT
	elif os.path.exists(DEV_CDR_DEFAULT) is True:
		device = DEV_CDR_DEFAULT
	
	if device is not None:
		device = os.path.join(os.path.dirname(device), os.readlink(device))
	
	return device

# ************** verifyImage *****************
def verifyImage(isoFile, md5File):
	"""verifies that the ISO image File's MD5 sum matches the alleged sum.
	
	Note: The sum is calculated using the linux program md5sum.
	
	Parameters:
	isoFile -- a string path to the ISO image in question
	md5File -- a string path to a file containing the MD5 sum that the isoFile is supposed to match

	Returns: 
	True -- if the hash of isoFile matches allegedSum 
	False -- otherwise
	
	"""
	
	p = Popen("md5sum -c " + md5File + " | grep -v 'OK$'", shell=True, stdout=PIPE)
	output = strip(p.communicate()[0])
	if output is None or len(output) is 0:
		return True
	else:
		return False

# ************** verifyDisc *****************
def verifyDisc(mountPoint):
	"""verifies that a disc's MD5 sum matches the sums contained in the root folder
	of the CD. 

	Note: This function is intended for use on Ubunutu Linux CDs, as in their root
	they contain a file called md5sum.txt, containing MD5s of the disc's contents
	The verification is done using the linux program md5sum.

	Parameters:
	mountPoint -- A string containing the mount point of the disc

	Returns:
	True -- if the data of the disc mounted at mountPoint was verified by md5sum
	False -- otherwise
	
	"""

	os.chdir(mountPoint);
	p = Popen("md5sum -c md5sum.txt | grep -v 'OK$'", shell=True, stdout=PIPE)
	output = strip(p.communicate()[0])
	if output is None or len(output) is 0:
		return True
	else:
		return False

# ************** burn *****************
def burn(isoFile, device=None, isRealBurn=False, ejectAfter=False, speed=None):
	"""burns a CD of the specified ISO image using the specified device

	Note: This function uses the linux program wodim to do the actual burning.

	Parameters:
	isoFile -- the ISO image to burn
	device -- a device capable of burning CDs. If no device is specified (device=None), wodim will search for a default one and use that
	isRealBurn -- a boolean value determining if the disc should actually be burned or just go through a test run  (default=False)
	ejectAfter -- a boolean value determining if the disc should be ejected immediately after the burn process completes (default=False)
	speed -- a number representing the speed factor at which to burn the disc. If set to None, wodim will use the burning device's maximum speed (default=None)

	Returns:
	an integer representing the exit code of wodim. A successful burn will return 0
	
	"""

	cmd = WODIM_BURN_CMD
	if device != None:
		cmd = cmd + WODIM_DEV_ARG + device
	if speed != None:
		cmd = cmd + WODIM_SPEED_ARG + str(speed)
	if isRealBurn is False:
		cmd = cmd + WODIM_DUMMY_ARG
	if ejectAfter is True:
		cmd = cmd + WODIM_EJECT_ARG

	cmd = cmd + " " + isoFile
	p = Popen(cmd, shell=True, stdout=PIPE)
	output = p.communicate()[0]
	returnCode = p.returncode
	return returnCode

#****************************
def waitForDiscMount(device, maxWait=0):
	"""blocks program execution until the specified device has been mounted

	Parameters:
	device -- a string of the path to the device whose mounting is to be tested
	maxWait -- the maximum amount of time in seconds that the program should wait before giving up. A value of 0 means to wait indefinitely (default=0)
	
	Returns:
	a string containing the path to the point in the filesystem to where the device was mounted. If the device has not been mounted, an empty string will be returned 
	
	"""

	output = None

	if maxWait <= 0: 
		timeLeft = 1
	else:
		timeLeft = maxWait

	mntDir = ""

	while timeLeft > 0:
		mntDir = getDiscMountPoint(device)
		if len(mntDir) > 0: break
		if maxWait > 0: 
			timeLeft = timeLeft - 1
		time.sleep(1)
	
	return mntDir

def getDiscMountPoint(device):
	"""returns the mount point of the specified device
	
	Parameters:
	device -- a string of the path to the device in question
	
	Returns:
	a string containing the path to the point in the filesystem to where the device was mounted. If the device has not been mounted, an empty string will be returned 
	
	"""

	mntDir = ""
	p = Popen("mount | grep '" + device + "'", shell=True, stdout=PIPE)
	output = p.communicate()[0]
	if output != None and output != "": 
		elements = split(output)
		if len(elements) >= 3: # mount gives us '/dev/scd0 on /media/cdrom0'
			mntDir = elements[2]
	return strip(mntDir)
#****************************

def getCDVolumeName(device):
	"""returns the volume name of the disc contained in the specified device

	Parameters:
	device -- a string of the path to the device where the disc has been inserted

	Returns:
	a string containing the volume name of the disc

	"""

	if isMediaInserted(device) is False: return None # early quit if no media
	p = Popen(VOLNAME_CMD + device + " | grep -v 'No medium'", shell=True, stdout=PIPE, stderr=PIPE)
	data = p.communicate()
	output = data[0]
	err = data[1]

	name = strip(output)
	if name == "": name = None

	return name


#****************************

def getCDDeviceDescriptor(device):
	"""returns a file descriptor to the specified device
	"""

	try:
		drive = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
	except:
		drive = -1
	return drive

#****************************

def openTray(device=""):
	"""issues an eject command to open the tray the specified device. 

	If no device is specified, the default name "cdrom" will be used

	"""

	p = Popen(TRAY_OPEN_CMD + device, shell=True, stdout=None)


def closeTray(device=""):
	"""issues an eject command to close the tray of the specified device. 

	If no device is specified, the default name "cdrom" will be used

	"""
	p = Popen(TRAY_CLOSE_CMD + device, shell=True, stdout=None)


def queryDrive(device):
	"""issues an ioctl command for the status of the drive specified by the device

	WARNING: Linux Kernels 2.6.24 and before contain a bug where the drive will
	always report the tray as being open unless a disc is inside.

	Returns:
	a status code of the drive. These codes are enumerated in the dictionary CD_STATUS

	"""
	drive = getCDDeviceDescriptor(device)
	status = fcntl.ioctl(drive, IOCTL_CDROM_DRIVE_STATUS, 0)
	os.close(drive)
	return status


def queryDisc(device):
	"""issues an ioctl command for the status of the disc contained in the drive specified by the device

	Returns:
	a status code of the disc. These codes are enumerated in the dictionary CD_STATUS

	"""

	drive = getCDDeviceDescriptor(device)
	status = fcntl.ioctl(drive, IOCTL_CDROM_DISC_STATUS, 0)
	os.close(drive)
	return status


def isTrayOpen(device):
	"""issues an ioctl command for the status of the drive's tray status

	WARNING: Linux Kernels 2.6.24 and before contain a bug where the drive will
	always report the tray as being open unless a disc is inside.
	If you are only testing for the presence of media, 
	a safer option would be to use the function isMediaInserted

	Parameters:
	device -- a string of the path to the desired device

	Returns:
	True -- if the tray is open
	False -- if the tray is not open (closed, no tray)
	"""

	drive = getCDDeviceDescriptor(device)
	status = fcntl.ioctl(drive, IOCTL_CDROM_DRIVE_STATUS, 0)
	os.close(drive)
	return (status == CD_STATUS['TRAY_OPEN'])


def isBlankInserted(device):
	"""issues an ioctl command for the status of the drive and disc,
	and based on these values determines if a blank CD has been inserted

	Parameters:
	device -- a string of the path to the desired device

	Returns:
	True -- if the drive contains a blank CD
	False -- otherwise
	
	"""

	drive = getCDDeviceDescriptor(device)

	driveStatus = fcntl.ioctl(drive, IOCTL_CDROM_DRIVE_STATUS, 0)
	discStatus = fcntl.ioctl(drive, IOCTL_CDROM_DISC_STATUS, 0)
	os.close(drive)

	status = driveStatus | discStatus

	return isMediaInserted(device) and (status == BLANK_CD_STATUS)


def waitForMedia(device, maxWait=0):
	"""suspends program execution until a CD has been inserted into the drive

	Parameters:
	device -- a string of the path to the desired device
	maxWait -- the maximum amount of time in seconds that the program should wait before giving up. A value of 0 means to wait indefinitely (default=0)
	
	"""
	if maxWait <= 0: 
		timeLeft = 1
	else:
		timeLeft = maxWait

	while timeLeft > 0:
		currState = getMediaChangedState(device)
		if currState is CD_MEDIA_PRESENT: break
		if maxWait > 0: 
			timeLeft = timeLeft - 1
		time.sleep(1)
	
	return


def isMediaInserted(device):
	"""issues an iotctl command to detect if there is a CD in the drive based
	on the MEDIA_CHANGED_STATE, not drive or disc status
	
	Parameters:
	device -- a string of the path to the desired device

	Returns:
	True -- if there is media present in the drive
	False -- otherwise

	"""
	status = getMediaChangedState(device)
	return status == CD_MEDIA_PRESENT

# Queries the drive as to whether or not the media has changed
# to check for a change, query once, then query for a change in that
# status. From tests, it appears to return 1 if there is no media inserted, 
# and 0 if media is present. Therefore, this function could
# also be used to check if media exists in the drive.
def getMediaChangedState(device):
	"""issues an iotctl command to detect if the media in the drive has changed

	Parameters:
	device -- a string of the path to the desired device
	
	Returns:
	0 -- if there is media present in the device
	1 -- otherwise
	"""

	drive = getCDDeviceDescriptor(device)
	status = fcntl.ioctl(drive, IOCTL_CDROM_MEDIA_CHANGED, 0)
	os.close(drive)
	return status

#******************************************************************************
# Test Burn
# usage: pywodim.py [OPTIONS] [ISOFILE]
#******************************************************************************

def printVersion():
	print "pywodim" + __version__
	print "Copyright (C) 2008 Jess Bermudes"
	print "License GPLv2+: GNU GPL version 2 or later <http://gnu.org/licenses/gpl.html>"
	print "This is free software: you are free to change and redistribute it."
	print "There is NO WARRANTY, to the extend permitted by law."
	print
	print "Written by Jess Bermudes"

def printHelp():
	print "USAGE: pywodim.py [OPTIONS] [ISOFILE]"
	print "Burn a CD and ensure its data integrity using wodim"
	print
	print "OPTIONS:"
	print "  --dev\t\t\tthe target burning device"
	print "  --pre\t\t\tpre-burn verification of FILE's MD5 sum"
	print "  --post\t\tpost-burn verification of disc's MD5 sum"
	print "  --dummy\t\tturns off drive's laser for test burn"
	print "  --help\t\tdisplay this help and exit"
	print "  --version\t\toutput version information and exit"
	print
	exit(os.EX_USAGE)

if len(sys.argv) < 2:
	printHelp()
	exit(os.EX_USAGE)

args = sys.argv
numArgs = len(args)

targetDev = ""
isoFile = ""
md5File = ""
devFlag = False
preFlag = False
postFlag = False
dummyFlag = False

if string.find(args[numArgs-1], "-", 0, 1) < 0:
	isoFile = args[numArgs-1]
else:
	print "ERROR: last argument is not FILE. See --help for more information."
	exit(os.EX_USAGE)

for i in range(1, numArgs):
	arg = args[i]
	
	if arg == "--dev":
		devFlag = True
		if i == numArgs - 1: # if dev is the last flag
			print "ERROR: No device specified"
			exit(os.EX_USAGE)
		else:
			targetDev = args[i+1]
	elif arg == "--pre":
		preFlag = True
	elif arg == "--post":
		postFlag = True
	elif arg == "--dummy":
		dummyFlag = True
	elif arg == "--help":
		printHelp()
	elif arg == "--version":
		printVersion()
	elif i < numArgs - 1:
		print "pywodim: unrecognized option `" + arg + "'"
		print "See --help for more information."
			
if os.path.exists(isoFile) is False:
	print "ERROR: could not find file " + isoFile
	exit(1)

if devFlag is True and os.path.exists(targetDev) is not True:
	print "ERROR: could not find device " + targetDev

if targetDev == "":
	targetDev = getDefaultDevice()
	
if targetDev == None:
	print "ERROR: No CD Burning device detected."
	exit(1)

if preFlag is True:
	md5File = isoFile + ".md5"
	if os.path.exists(md5File) is not True:
		print "ERROR: could not find the MD5 file for the ISO specified"
		exit(1)

#exit()

# ****** STEP 1: Verify Image to be written ******
if preFlag is True:
	print "Verifying Image..."
	dataOK = verifyImage(isoFile, md5File)
	if dataOK is True:
		print "ISO Image OK."
	else:
		print "ERROR: ISO Image MD5 sum incorrect. Aborting..."
		exit(1)
	time.sleep(1)
	print
# ***

print "Opening tray..."
openTray(targetDev)
time.sleep(3)

blankInserted = False

# ****** Step 2: Wait for blank CD ******
while blankInserted is False:
	print "Insert blank CD..."
	waitForMedia(targetDev)
	print "Reading disc..."
	
	blankInserted = isBlankInserted(targetDev)
	if blankInserted == False:
		print "No blank disc detected! If you inserted a disc, it might have existing data."
		time.sleep(1)
		print "Ejecting disc..."
		openTray()
		time.sleep(3)
		print

print "Blank CD detected."
time.sleep(1)
print
# ***

# ****** Step 3: Burn CD ******
print "Burning CD..."
time.sleep(1)

burnCode = 0#burn(isoFile, targetDev, True, False) # burn=y, eject=n
time.sleep(3) # give a chance for the disc to spin down

if burnCode is WODIM_EXIT_CODE_SUCCESS:
	print "Disc burned."
else:
	print "There was an error in the burning process. See output above."
	print "Aborting..."
	exit(1)
# ***

time.sleep(1)
print

# ****** Step 4: Check data integrity ******
if postFlag is True:
	print "A data integrity test will now be performed."
	print
	time.sleep(1)
	print "First, the disc will be ejected."
	openTray(targetDev)
	time.sleep(3)

	discInserted = False

	while discInserted is False:
		print "Please re-insert media..."
		time.sleep(1)
		waitForMedia(targetDev)
		print "Waiting for system to mount disc..."
		mntDir = waitForDiscMount(targetDev, 30)
		if mntDir is None or len(mntDir) <= 0:
			print "Could not read disc. (No mount point detected)"
		else:
			discInserted = True

	print "Disc detected. Mounted at " + mntDir
	time.sleep(1)
	print

	print "Verifying disc integrity..."
	discOK = verifyDisc(mntDir)
	time.sleep(3) # Let's give the disc a chance to spin down

	if discOK is True:
		print "No errors found on disc."
	else:
		print "WARNING: Disc data contains errors!"

	time.sleep(6)
	print
# ***

# ****** Step 5: Eject disc ******
print "Ejecting disc..."
time.sleep(1)
openTray(targetDev)
time.sleep(3)
print
# ***

print "Burning complete."



