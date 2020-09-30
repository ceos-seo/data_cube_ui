# CEOS Open Data Cube UI

The CEOS Data Cube UI is a full stack Python web application used to perform analysis on raster datasets using the [Open Data Cube](https://www.opendatacube.org/). Using common and widely accepted frameworks and libraries, our UI is a good tool for demonstrating the Open Data Cube's capabilities and some possible applications and architectures. The UI's core technologies are:
* [**Django**](https://www.djangoproject.com/): Web framework, ORM, template processor, entire MVC stack
* [**Celery + Redis**](http://www.celeryproject.org/): Asynchronous task processing
* [**Open Data Cube**](http://datacube-core.readthedocs.io/en/stable/): API for data access and analysis
* [**PostgreSQL**](https://www.postgresql.org/): Database backend for both the Data Cube and our UI
* [**Apache/Mod WSGI**](https://en.wikipedia.org/wiki/Mod_wsgi): Standard service based application running our Django application while still providing hosting for static files
* [**Bootstrap3**](http://getbootstrap.com/): Simple, standard, and easy front end styling

Using these common technologies provides a good starting platform for users who want to develop Data Cube applications. Using Celery allows for simple distributed task processing while still being performant. Our UI is designed for high level use of the Data Cube and allow users to:
* Access various datasets that we have ingested
* Run custom analysis cases over user defined areas and time ranges
* Generate both visual (image) and data products (GeoTiff/NetCDF)
* Provide easy access to metadata and previously run analysis cases

Currently supported applications include:
* Cloud coverage (not enabled by default)
* Coastal change
* Custom mosaics (e.g. geometric median composite RGB images)
* Fractional cover
* Spectral anomaly (NDVI, NDWI, NDBI, etc.)
* Spectral indicies (NDVI, NDWI, NDBI, etc.)
* Water quality (total suspended matter)
* Urbanization (NDBI-NDVI-NDWI false-color composites)
* Water detection (using the [Water Observations from Space](https://www.ga.gov.au/scientific-topics/community-safety/flood/wofs) algorithm)

## Installation
-------

First follow the instructions in the [Docker Installation Guide](docs/docker_install.md) if you do not have Docker installed yet.

Follow the instructions in the 
[Open Data Cube Database Installation Guide](docs/odc_db_setup.md) to setup the Open Data Cube (ODC) database.

Follow the instructions in the [Open Data Cube UI Installation Guide](docs/ui_install.md) to install the ODC UI. That document also contains troubleshooting information for the UI in the form of an FAQ at the end.

Follow the instructions in the [Open Data Cube UI Algorithm Addition Guide](docs/adding_new_pages.md) to add new applications to the ODC UI. This guide is only intended for programmers.

## Obtaining Help
-------

If you encounter issues with Open Data Cube or this UI that are not documented in the documents linked to above or the other files in the `docs` directory (remember to check the FAQ sections) and you are unable to diagnose and fix those issues on your own, follow these steps to obtain assistance:
1. Search for your question in the [GIS Stack Exchange](https://gis.stackexchange.com/) with the `open-data-cube` tag. You can find such tagged questions [here](https://gis.stackexchange.com/questions/tagged/open-data-cube). If a question similar to yours has already been asked, search for a suitable answer in that question's webpage. If you can not find a suitable answer, contine to step 2. If no such question exists or if the question is missing some information that you think may be important regarding your issue, create a new question with the `open-data-cube` tag.
2. State your problem in the [ODC Slack workspace](http://slack.opendatacube.org/) in the most appropriate channel (use that link to join the workspace if you have not already). Use the **#general** channel if no other channel is more appropriate for your question. Link to the question on GIS Stack Exchange. When you receive an answer, add that answer to the question page on GIS Stack Exchange if the answerer is not available to do so. This preserves the answer in a publicly searchable way - which is useful for remembering answers to one's own past questions and benefits the community.

## More
-------

You may also consider running a Jupyter Notebook server that uses the Open Data Cube. The CEOS ODC Notebooks repository is [here](https://github.com/ceos-seo/data_cube_notebooks).