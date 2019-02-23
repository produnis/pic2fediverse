# pic2fediverse
A collection of picture bots for federation and fediverse written in python.

This scripts post pictures from a given directory to a given Fediverse-account. They post one picture per round.


## Diaspora
`pic2diaspora.py` - posts pictures from a given directory to a given Disapora-Account. It posts one picture per round. It requires https://github.com/marekjm/diaspy 

## Friendica
`pic2friendica.py` - posts pictures from a given directory to a given Friendica-Account. It posts one picture per round. 


## Mastodon
`pic2mastodon.py` - posts pictures from a given directory to a given Mastodon-Account. It posts one picture per round. It uses a bot access key for login and post. You can use e.g. https://takahashim.github.io/mastodon-access-token/ to generate your access key.

## General
You need to edit the scripts to fit your account-login-settings.

The scripts will create the file "`0archive_mastodon.txt`" / "`0archive_friendica.txt`" / "`0archive_diaspora.txt`" (depending on what script you use) in the given picture directory (check for write permission). In this textfiles, filenames of pictures already posted are stored. The scripts look up all pictures in the given directory and compare their filenames with "`0archive_*.txt`". The scripts won't upload any pictures with filenames included in "`0archive_*.txt`". The scripts will post the first "new" picture they find to mastodon/friendica/diaspora, write the filename into "`0archive_*.txt`" and exit. 

If there is a `.txt`-file with the same basename as the picture-file (e.g. "`picture1.jpg`" and "`picture1.txt`"), the txt-file's content will be posted as a Text along with the picture. 

So, one picture is posted per round. Thus, the scripts are ment to be run via cronjob.
```
  # Cron.Example:
  # post every 6 hours a picture
  0 */6 * * * 	cd /path/to/picturefolder; /path/to/pic2mastodon.py```
