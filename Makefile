NAME=spiff
PACKAGE=$(NAME)-$(VERSION)
VERSION="`python -c 'import os; os.chdir("src"); import config; print config.__version__'`"
PUBLISH_PATH=/home/sab/backups/code/www/test.debain.org/$(NAME)
PUBLISH_HOST=root@debain.org
DEPENDS=pywsgi spiff-signal spiff-guard spiff-integrator spiff-warehouse spiff-wikimarkup
DISTDIR=/pub/code/releases/$(NAME)

clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f
	rm -Rf $(PACKAGE)

dev-env:
	mkdir -p $(NAME)
	cd $(NAME); for PKG in $(NAME) $(DEPENDS); do \
		svn checkout http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
	done

dev-env-git:
	mkdir -p $(NAME)
	cd spiff; for PKG in $(NAME) $(DEPENDS); do \
		git svn init http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
		cd $$PKG; \
		git svn fetch; \
		cd -; \
	done

dist-prepare: clean
	mkdir -p $(PACKAGE)
	ls -1d * .htaccess | grep -v $(PACKAGE) | while read i; do cp -r "$$i" $(PACKAGE); done

full-dist-prepare: dist-prepare
	LIBDIR=$(PACKAGE)/src/libs; \
	mkdir -p $$LIBDIR; \
	for DEP in $(DEPENDS); do \
		rsync -ar ../$$DEP $$LIBDIR --exclude "*.git*"; \
	done

dist: dist-prepare
	tar cjf $(PACKAGE).tar.bz2 $(PACKAGE)
	make clean
	mkdir -p $(DISTDIR)/
	mv $(PACKAGE).tar.bz2 $(DISTDIR)

full-dist: full-dist-prepare
	tar cjf $(PACKAGE)-full.tar.bz2 $(PACKAGE)
	make clean
	mkdir -p $(DISTDIR)/
	mv $(PACKAGE)-full.tar.bz2 $(DISTDIR)

publish: full-dist-prepare
	rsync -azr $(PACKAGE)/src/ $(PUBLISH_HOST):$(PUBLISH_PATH)/
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/"
	make clean
