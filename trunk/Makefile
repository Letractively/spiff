NAME=spiff
VERSION=`python -c 'import os; os.chdir("src"); import config; print config.__version__'`
PACKAGE=$(NAME)-$(VERSION)-1
PUBLISH_PATH=/home/sab/backups/code/www/test.debain.org/$(NAME)
PUBLISH_HOST=root@debain.org
DISTDIR=/pub/code/releases/$(NAME)

###################################################################
# Project-specific targets.
###################################################################
DEPENDS=pywsgi spiff-signal spiff-guard spiff-integrator spiff-warehouse spiff-wikimarkup

svn-environment:
	mkdir -p $(NAME)
	cd $(NAME); for PKG in $(NAME) $(DEPENDS); do \
		svn checkout http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
	done

git-environment:
	mkdir -p $(NAME)
	cd spiff; for PKG in $(NAME) $(DEPENDS); do \
		git svn init http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
		cd $$PKG; \
		git svn fetch; \
		cd -; \
	done

dist-prepare:
	# Copy all files that are to be distributed into a subdirectory.
	mkdir -p $(PACKAGE)
	ls -1d * .htaccess \
		| grep -v $(PACKAGE) \
		| while read i; do \
		cp -r "$$i" $(PACKAGE); \
	done

	# Copy all dependencies.
	LIBDIR=$(PACKAGE)/src/libs; \
	mkdir -p $$LIBDIR; \
	for DEP in $(DEPENDS); do \
		rsync -ar ../$$DEP $$LIBDIR --exclude "*.git*"; \
	done

###################################################################
# Standard targets.
###################################################################
clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f
	rm -Rf $(PACKAGE)

dist-clean: clean
	rm -Rf $(PACKAGE)*

doc:
	# No docs yet.

install:
	# No such action. Please read the INSTALL file.

uninstall:
	# No such action. Please read the INSTALL file.

tests: dist-prepare
	rsync -azr $(PACKAGE)/src/ $(PUBLISH_HOST):$(PUBLISH_PATH)/
	ssh $(PUBLISH_HOST) "chown -R www-data:www-data $(PUBLISH_PATH)/"
	make clean

###################################################################
# Package builders.
###################################################################
targz: dist-prepare
	tar czf $(PACKAGE).tar.gz $(PACKAGE)
	make clean

tarbz: dist-prepare
	tar cjf $(PACKAGE).tar.bz2 $(PACKAGE)
	make clean

deb: dist-prepare
	# No debian package yet.
	make clean

dist: targz tarbz deb

###################################################################
# Publishers.
###################################################################
dist-publish: dist
	mkdir -p $(DISTDIR)/
	mv $(PACKAGE)* $(DISTDIR)

doc-publish: doc
