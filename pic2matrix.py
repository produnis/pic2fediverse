#!/usr/bin/env python3
##############################
# sudo pip3 install matrix-nio python-magic
##############################
import asyncio
import json
import os
import sys
import getpass
from PIL import Image
import aiofiles.os
import magic

from nio import AsyncClient, LoginResponse, UploadResponse
########################################################
#
# This script posts pictures from a given directory
# to a given Matrix-room. It posts one picture per round.
#
# Requires:
#		- python3
#		- matrix-nio python-magic
#
# Usage:
#		# script will fail if it is not called from picturefolder!!
#		$:>  cd /path/to/picturefolder
# 		$:>  /path/to/pic2matrix.py
#
# This script will create the file "0archive_matrix.txt"
# in the given picture directory (check for write permission). In this textfile,
# filenames of pictures already posted are stored.
# The script looks up all pictures in the given directory
# and compares their filenames with "0archive_matrix.txt".
# The script won't upload any pictures of filenames included in "0archive_matrix.txt"
# The script will post the first "new" pictures it finds to mastodon, writes the filename
# into "0archive_matrix.txt" and exits.
# If there is a .txt-file with the same basename as the picture-file (e.g. "picture1.jpg" and "picture1.txt")
# The txt-file's content will be posted as a Text along with the picture.
# So, one picture is posted per round. Thus, the script is ment to be run via cronjob.
#  # Cron.Example:
#  # post every 6 hours a picture
#  0 */6 * * * 	cd /path/to/picturefolder; /path/to/pic2matrix.py
#
#---------------------------------------------
# 		CHANGE TO FIT YOUR SETTINGS
#---------------------------------------------
room_id = "!UGziVBfWerjrNcWgXF:cactus.chat"     # The romm ID (NOT room name) of the matrix room to post to
standardmessage= "Jippi"                        # message posted with each photo, e.g. "#nsfw"

### no need to change anything from here...
########################################################

CONFIG_FILE = "credentials.json"

# Check out main() below to see how it's done.


def write_details_to_disk(resp: LoginResponse, homeserver) -> None:
    """Writes the required login details to disk so we can log in later without
    using a password.

    Arguments:
        resp {LoginResponse} -- the successful client login response.
        homeserver -- URL of homeserver, e.g. "https://matrix.example.org"
    """
    # open the config file in write-mode
    with open(CONFIG_FILE, "w") as f:
        # write the login details to disk
        json.dump(
            {
                "homeserver": homeserver,  # e.g. "https://matrix.example.org"
                "user_id": resp.user_id,  # e.g. "@user:example.org"
                "device_id": resp.device_id,  # device ID, 10 uppercase letters
                "access_token": resp.access_token  # cryptogr. access token
            },
            f
        )


async def send_image(client, room_id, image):
    """Send image to toom.

    Arguments:
    ---------
    client : Client
    room_id : str
    image : str, file name of image

    This is a working example for a JPG image.
        "content": {
            "body": "someimage.jpg",
            "info": {
                "size": 5420,
                "mimetype": "image/jpeg",
                "thumbnail_info": {
                    "w": 100,
                    "h": 100,
                    "mimetype": "image/jpeg",
                    "size": 2106
                },
                "w": 100,
                "h": 100,
                "thumbnail_url": "mxc://example.com/SomeStrangeThumbnailUriKey"
            },
            "msgtype": "m.image",
            "url": "mxc://example.com/SomeStrangeUriKey"
        }

    """
    mime_type = magic.from_file(image, mime=True)  # e.g. "image/jpeg"
    if not mime_type.startswith("image/"):
        print("Drop message because file does not have an image mime type.")
        return

    im = Image.open(image)
    (width, height) = im.size  # im.size returns (width,height) tuple

    # first do an upload of image, then send URI of upload to room
    file_stat = await aiofiles.os.stat(image)
    async with aiofiles.open(image, "r+b") as f:
        resp, maybe_keys = await client.upload(
            f,
            content_type=mime_type,  # image/jpeg
            filename=os.path.basename(image),
            filesize=file_stat.st_size)
    if (isinstance(resp, UploadResponse)):
        print("Image was uploaded successfully to server. ")
    else:
        print(f"Failed to upload image. Failure response: {resp}")

    content = {
        "body": os.path.basename(image),  # descriptive title
        "info": {
            "size": file_stat.st_size,
            "mimetype": mime_type,
            "thumbnail_info": None,  # TODO
            "w": width,  # width in pixel
            "h": height,  # height in pixel
            "thumbnail_url": None,  # TODO
        },
        "msgtype": "m.image",
        "url": resp.content_uri,
    }

    try:
        await client.room_send(
            room_id,
            message_type="m.room.message",
            content=content
        )
        print("Image was sent successfully")
    except Exception:
        print(f"Image send of file {image} failed.")


async def main() -> None:
    # If there are no previously-saved credentials, we'll use the password
    if not os.path.exists(CONFIG_FILE):
        print("First time use. Did not find credential file. Asking for "
              "homeserver, user, and password to create credential file.")
        homeserver = "https://matrix.example.org"
        homeserver = input(f"Enter your homeserver URL: [{homeserver}] ")

        if not (homeserver.startswith("https://")
                or homeserver.startswith("http://")):
            homeserver = "https://" + homeserver

        user_id = "@user:example.org"
        user_id = input(f"Enter your full user ID: [{user_id}] ")

        device_name = "matrix-nio"
        device_name = input(f"Choose a name for this device: [{device_name}] ")

        client = AsyncClient(homeserver, user_id)
        pw = getpass.getpass()

        resp = await client.login(pw, device_name=device_name)

        # check that we logged in succesfully
        if (isinstance(resp, LoginResponse)):
            write_details_to_disk(resp, homeserver)
        else:
            print(f"homeserver = \"{homeserver}\"; user = \"{user_id}\"")
            print(f"Failed to log in: {resp} {pw}")
            sys.exit(1)

        print(
            "Logged in using a password. Credentials were stored.",
            "Try running the script again to login with credentials."
        )

    # Otherwise the config file exists, so we'll use the stored credentials
    else:
        picdir = os.getcwd()
        print('picture directory is %s' % (picdir))
        # check if there is my archive_posted.txt in picture directory
        archive_path = '%s/%s' % (picdir, '0archive_matrix.txt')
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
                    # post pic to Matrix
                    #--------------------
                    print('Upload pic %s with path %s to Matrix' % (pics, pic_path))
                    # open the file in read-only mode
                    with open(CONFIG_FILE, "r") as f:
                        config = json.load(f)
                        client = AsyncClient(config['homeserver'])
                        client.access_token = config['access_token']
                        client.user_id = config['user_id']
                        client.device_id = config['device_id']

                    await send_image(client, room_id, pics)
                    print("Logged in using stored credentials. Sent a test message.")
                    await client.room_send(
                        # Watch out! If you join an old room you'll see lots of old messages
                        room_id=room_id,
                        message_type="m.room.message",
                        content = {
                            "msgtype": "m.text",
                            "body": textmessage
                        }
                    )
                    #await client.sync_forever(timeout=30000) # milliseconds
                    # Close the client connection after we are done with it.
                    await client.close()
                    # write pic's filename to archive log
                    f=open(archive_path,"a")
                    f.write(pics)
                    f.write('\n')
                    f.close()
                    break
            else:
                print('This file has no valid suffix: %s' % (pics))
            print('\nDone!\n')

asyncio.get_event_loop().run_until_complete(main())
