#!/usr/bin/env python3
import os
from mastodon import Mastodon
import sys
########################################################
#
# This script posts pictures from a given directory
# to a given Mastodon-account. It posts one picture per round.
#
# Requires:
#		- python3
#		- Mastodon.py (https://github.com/halcy/Mastodon.py)
#
# Usage:
#		# script will fail if it is not called from picturefolder!!
#		$:>  cd /path/to/picturefolder							
# 		$:>  /path/to/pic2mastodon.py
#
# This script will create the file "0archive_mastodon.txt"
# in the given picture directory (check for write permission). In this textfile,
# filenames of pictures already posted are stored.
# The script looks up all pictures in the given directory
# and compares their filenames with "0archive_mastodon.txt".
# The script won't upload any pictures of filenames included in "0archive_mastodon.txt"
# The script will post the first "new" pictures it finds to mastodon, writes the filename into "0archive_mastodon.txt" and exits. 
# If there is a .txt-file with the same basename as the picture-file (e.g. "picture1.jpg" and "picture1.txt")
# The txt-file's content will be posted as a Text along with the picture.
# So, one picture is posted per round. Thus, the script is ment to be run via cronjob.
#  # Cron.Example:
#  # post every 6 hours a picture
#  0 */6 * * * 	cd /path/to/picturefolder; /path/to/pic2mastodon.py
#
#---------------------------------------------
# 		CHANGE TO FIT YOUR SETTINGS
#---------------------------------------------
podurl 		= 'https://mastodon.url'	# The URL of your account's pod
standardmessage = '#cool #hastags '		# message posted with each photo, e.g. "#nsfw"
visibility 	= "public"			# "direct", "private", "unlisted", "public"
access_token 	= "YY XX ZZ " 			# The acces-token is needed to login/post to your account
						# You can e.g. use https://takahashim.github.io/mastodon-access-token/
						# to generate your access-key.
#---------------------------------------------
#########################################################
# no need to change anything after here
#---------------------------------------------


# # #    M A I N    L O O P    # # # #
#---------------------------------------------
#
picdir = os.getcwd()
print('picture directory is %s' % (picdir))

mastodon = Mastodon(
    access_token = access_token,
    api_base_url = podurl 
)


# check if there is my archive_posted.txt in picture directory
archive_path = '%s/%s' % (picdir, '0archive_mastodon.txt')
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
	if pics.lower().endswith(('.png', '.jpg', '.gif', '.mp4', '.jpe', '.jpeg')):
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
				
			# post pic to mastodon
			print('Upload pic %s with path %s to Mastodon' % (pics, pic_path))
			mastopicid = mastodon.media_post(media_file = pics, description=textmessage)
			mastodon.status_post(status=textmessage, media_ids=mastopicid['id'], visibility=visibility)
			# write pic's filename to archive log
			f=open(archive_path,"a")
			f.write(pics)
			f.write('\n')
			f.close()
			break
	else:
		print('This file has no valid suffix: %s' % (pics))
print('\nDone!\n')
