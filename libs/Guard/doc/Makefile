HANDBOOKS=guard.de.latex

all: handbook apidocs

handbook:
	# Run twice, required to resolve references.
	for FILE in $(HANDBOOKS); do \
		pdflatex -halt-on-error $$FILE && pdflatex $$FILE; \
		LOCALE=`echo $$FILE | sed 's/[^\.]*\.//; s/\..*//'`; \
		latex2html -nonavigation -split 0 -html_version 4.0,unicode -mkdir -dir handbook.$$LOCALE $$FILE; \
	done

apidocs:
	python mkapidoc.py

clean:
	rm -Rf api handbook.*
	rm -f *.aux *.log *.toc *.pdf

publish: handbook apidocs
	scp -r handbook.* *.pdf api/* kd10243@goliath.speedpartner.de:/home/kd10243/spiff.debain.org/static/docs/spiff_guard/
