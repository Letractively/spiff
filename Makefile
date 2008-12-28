PUBLISH_PATH=/home/sab/backups/code/www
PUBLISH_HOST=root@debain.org

publish-cgi:
	rsync -azr . $(PUBLISH_HOST):$(PUBLISH_PATH)/spiff-test-cgi.debain.org/ \
				--exclude /.git
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/spiff-test-cgi.debain.org/"

publish-mp:
	rsync -azr . $(PUBLISH_HOST):$(PUBLISH_PATH)/spiff-test-mp.debain.org/ \
				--exclude /.git
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/spiff-test-mp.debain.org/"

publish: publish-mp publish-cgi
