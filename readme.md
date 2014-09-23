#St Andrews Observatory Project Backend

This backend has two functions. It can a) scrape weather from sources into an archive and b) parse fits files for display on the frontend.

## Deployment

The main deployment steps are based on resolving dependancies.

clone repo

	git clone https://github.com/billytrend/st-andrews-observatory-backend.git

install f2n

	svn export https://svn.epfl.ch/svn/mtewes-public/trunk/f2n ./f2n
	cd f2n/
	python setup.py install
	cd ../
	rm -r f2n/

install pip dependancies

	pip install xmltodict
	pip install feedparser
	apt-get install python-lxml
	pip install lxml
	pip install astropy
	pip install scipy
	pip install pyfits
	pip install numpy

install pillow

*make sure this includes the version 2.4.0 more recent versions have a critical bug in them*

	pip install pillow==2.4.0  


add a data folder (should be at the web app root)

	mkdir ??/data


## Usage

First initialise the data folder in the web app root.

	python src/main.py -i ??/path_to_fits_file_repo ??/data
	
This will set all the current fits files to ignore so *only new* fits files will be parsed - may make it appear as though the site isn't working until the first fits files come through.

### Cron jobs

Parses latest weather forecasts to the data folder

	python src/main.py -w ??/data
	
Parses latest fits files to data folder. Does nothing if there are no new files.

	python src/main.py -f ??/path_to_fits_file_repo ??/data

## Troubleshooting

	* Check missing dependancies
	* Check pillow is on the right version
	* Check that the apis are still at the right version
	* Let me (wt6@st-andrews.ac.uk) know if there are problems. I'll be happy to help.