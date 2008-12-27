publish:
	rsync -avzr . root@91.184.35.4:/home/sab/backups/code/www/spiff.debain.org/spiff/ \
				--exclude /.git
	ssh root@91.184.35.4 "chown -R www-data:www-data /home/sab/backups/code/www/spiff.debain.org/"
