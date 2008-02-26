HANDBOOKS=en de

all: handbook apidocs

pdf:
	# Run each call of pdflatex twice, required to resolve references.
	for LOCALE in $(HANDBOOKS); do \
		FILE=guard.$$LOCALE; \
		pdflatex -halt-on-error $$FILE.latex && pdflatex $$FILE.latex; \
		rm $$FILE.aux $$FILE.log $$FILE.out $$FILE.toc; \
		[ ! -e handbook/$$LOCALE ] && mkdir -p handbook/$$LOCALE/; \
		mv $$FILE.pdf handbook/$$LOCALE/spiff_guard.$$LOCALE.pdf; \
	done

handbook: pdf
	for LOCALE in $(HANDBOOKS); do \
		FILE=guard.$$LOCALE; \
		latex2html -nonavigation -toc_depth 5 -split 0 -html_version 4.0,unicode -mkdir -dir handbook/$$LOCALE/ $$FILE.latex; \
	done

apidocs:
	python mkapidoc.py

clean:
	rm -Rf api handbook
	rm -f *.aux *.log *.out *.pdf *.toc

publish: handbook apidocs
	scp -r handbook/* api/* kd10243@goliath.speedpartner.de:/home/kd10243/spiff.debain.org/static/docs/spiff_guard/
