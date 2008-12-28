PUBLISH_PATH=/home/sab/backups/code/www
PUBLISH_HOST=root@debain.org

publish-cgi:
	rsync -azr src/ $(PUBLISH_HOST):$(PUBLISH_PATH)/spiff-test-cgi.debain.org/
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/spiff-test-cgi.debain.org/"

publish-mp:
	rsync -azr src/ $(PUBLISH_HOST):$(PUBLISH_PATH)/spiff-test-mp.debain.org/
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/spiff-test-mp.debain.org/"

publish: publish-mp publish-cgi
