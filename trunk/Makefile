PUBLISH_PATH=/home/sab/backups/code/www
PUBLISH_HOST=root@debain.org
VERSION="`python -c 'import os; os.chdir("src"); import config; print config.__version__'`"
PACKAGE_NAME=spiff-$(VERSION)
DEPENDS=pywsgi spiff-signal spiff-guard spiff-integrator spiff-warehouse

clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f
	rm -Rf $(PACKAGE_NAME)

dev-env:
	mkdir -p spiff
	cd spiff; for PKG in spiff $(DEPENDS); do \
		svn checkout http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
	done

dev-env-git:
	mkdir -p spiff
	cd spiff; for PKG in spiff $(DEPENDS); do \
		git svn init http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
		cd $$PKG; \
		git svn fetch; \
		cd -; \
	done

dist-prepare: clean
	mkdir -p $(PACKAGE_NAME)
	ls -1d * .htaccess | grep -v $(PACKAGE_NAME) | while read i; do cp -r "$$i" $(PACKAGE_NAME); done

dist: dist-prepare
	tar cjf $(PACKAGE_NAME).tar.bz2 $(PACKAGE_NAME)
	make clean

full-dist-prepare: dist-prepare
	LIBDIR=$(PACKAGE_NAME)/src/libs; \
	mkdir -p $$LIBDIR; \
	for DEP in $(DEPENDS); do \
		rsync -ar ../$$DEP $$LIBDIR --exclude "*.git*"; \
	done

full-dist: full-dist-prepare
	tar cjf $(PACKAGE_NAME)-full.tar.bz2 $(PACKAGE_NAME)
	make clean

publish-cgi: full-dist-prepare
	rsync -azr $(PACKAGE_NAME)/src/ $(PUBLISH_HOST):$(PUBLISH_PATH)/spiff-test-cgi.debain.org/
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/spiff-test-cgi.debain.org/"
	make clean

publish-mp: full-dist-prepare
	rsync -azr $(PACKAGE_NAME)/src/ $(PUBLISH_HOST):$(PUBLISH_PATH)/spiff-test-mp.debain.org/
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/spiff-test-mp.debain.org/"
	make clean

publish:
	make publish-mp
	make publish-cgi
