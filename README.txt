To run this, you'll need to install some modules and dictionary files.

This assumes you've made a virtualenv and are working in it.

The easy way:
	Run install.sh 

The hard way:
	Run `pip install -r requirements.txt`
	Open a Python shell
	Run `import nltk`, then run `nltk.download()`.
	Download WordNet from the Corpora tab, then the actual app should run.

You can start Celery by running the celery.sh file.
