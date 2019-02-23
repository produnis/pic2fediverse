#!/usr/bin/env python3
import os
import diaspy
import sys
########################################################
#
# This script posts pictures from a given directory
# to a given DIASPORA-Account. It posts one picture per round.
# Subfolders are not supported.
#
# Requires:
#		- python3
#		- diaspy   (do a manual install via https://github.com/marekjm/diaspy)
#
# Usage:
#		# script will fail if it is not called from picturefolder!!
#		$:>  cd /path/to/picturefolder							
# 		$:>  /path/to/pic2diaspora.py
#
# This script will create the file "0archive_diaspora.txt"
# in the given picture directory (check for write permission). 
# In this textfile, filenames of pictures already posted are stored.
#
# The script looks up all pictures in the given directory
# and compares their filenames with "0archive_diaspora.txt"
# This script won't upload any pictures included in "0archive_diaspora.txt"
# The script will take the first "new" pictures it finds, post it to Diaspora and exit. 
# If there is a .txt-file with the same basename as the picture-file (e.g. "picture1.jpg" and "picture1.txt")
# The txt-file's content will be posted along with the picture.
# 
# So, one picture is posted per round. Thus, the script is ment to be run via cronjob.
#  # Cron.Example:
#  # post a picture every 6 hours 
#  0 */6 * * * 	cd /path/to/picturefolder; /path/to/pic2diaspora.py 
#
#---------------------------------------------
# 		CHANGE TO FIT YOUR SETTINGS
#---------------------------------------------
podurl 		= 'https://your.pod.org' 	# The URL of your account's pod
poduser 	= 'USERNAME'				# Username	
poduserpwd 	= 'SUPERSECRET'				# Password
standardmessage = '#cool #hashtags'		# message posted with each photo, e.g. "#nsfw"
aspect_to_post  = "public" 				# ids of aspects to post to, eg. = (4520, 4521) 

#---------------------------------------------
#########################################################
# no need to change anything after here
#---------------------------------------------


# # #    M A I N    L O O P    # # # #
#---------------------------------------------
#
picdir = os.getcwd()
print('picture directory is %s' % (picdir))


# check if there is my archive_posted.txt in picture directory
archive_path = '%s/%s' % (picdir, '0archive_diaspora.txt')
print(archive_path)
ismylogthere = os.path.exists(archive_path)
if ismylogthere == False:
	print('creating my archive-log in %s' % (archive_path))
	f=open(archive_path,"w")
	f.close()


# read already posted pics from archive_posted.txt
archiveposted = open(archive_path).read()


# read all filenames in picture directory
pictures = os.listdir(picdir)
for pics in pictures:
	# check if this pic is really a pic
	if pics.lower().endswith(('.png', '.jpg', '.gif', '.jpe', '.jpeg')):
		# check if pic was already posted
		if pics in archiveposted:
			print('picture already posted: %s' % (pics))
		else:
			print('Ready to post new picture: %s' % (pics))
			pic_path = '%s/%s' % (picdir, pics)
			
			# check if there is a .txt for a message to post with this pic
			pic_base = os.path.splitext(pic_path)[0] # remove picture suffix from filename
			pic_txtfile  = "%s.txt" % (pic_base)     # add .txt
			print("Looking for txt-file %s \n" % (pic_txtfile))
			if os.path.exists(pic_txtfile) == True:
				print("Found txt file!\n")
				pic_txt = open(pic_txtfile).read()
				textmessage= '%s \n %s' % (pic_txt, standardmessage)
			else:
				print("No txt-file found. Posting Image only\n")
				textmessage=standardmessage
	
			# post pic to diaspora
			print('Upload pic %s with path %s to Diaspora' % (pics, pic_path))
			connection = diaspy.connection.Connection(pod=podurl, username=poduser, password=poduserpwd)
			connection.login()
			token = repr(connection)
			stream = diaspy.streams.Stream(connection)
			stream.post(photo=pics, text=textmessage, aspect_ids=aspect_to_post)
			
			# write pic's filename to archive log
			f=open(archive_path,"a")
			f.write(pics)
			f.write('\n')
			f.close()
			break
	else:
		print('This file has no valid suffix: %s' % (pics))
print('\nDone!\n')
