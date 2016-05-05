#!/usr/bin/python

from flask import Flask, render_template, request, url_for, redirect
from celery import Celery
from nltk.corpus import wordnet as wn
from wikimarkup import parse
from time import sleep
import wikipedia, random, json

app = Flask(__name__, static_url_path='')
app.debug = True
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/')
def index():
#    return app.send_static_file('index.html')
     return render_template("index.html")

@app.route('/make', methods=['POST'])
def make():
	articleid = request.form["articleid"]
	task = processarticle.delay(articleid)
	#return 'Job ID ' + task.id, 302, {'Location': url_for('progresspage', task_id = task.id)}
#	return "Original: \n\n" + wp.content + "\n\nNew: \n\n" + content + "\n\nChanged words: " + str(replacecount) + "\n\nLog:\n" + output
	return render_template('wait.html', taskid = task.id)

@app.route('/result/<task_id>')
def result(task_id):
	task = processarticle.AsyncResult(task_id)
	if task.state == 'SUCCESS':
		content = task.result['article']
		html = parse(content, False)
		return render_template("result.html", content = content, html = html, info = task.result['info'])
	else:
		return "Be more patient!"

@app.route('/status/<task_id>')
def progress(task_id):
	task = processarticle.AsyncResult(task_id)
	stat = ""
	curr = 0
	total = 100
	if task.state == 'PENDING':
		stat = "Job queued..."
	elif task.state == 'PROCESSING':
		stat = task.info['status']
		curr = task.info['current']
		total = task.info['total']
	elif task.state == 'SUCCESS':
		stat = task.info['status']
		return json.dumps({'progress': curr, 'status': stat, 'content': task.result['article'], 'info': task.result['info'], 'complete': 1})
	else:
		stat = 'An error occurred.'
	#return render_template("wait.html", status = stat, current = curr, total = total)
	return json.dumps({'percent': curr, 'status': stat, 'total': total, 'complete': 0})

@celery.task(bind=True)
def processarticle(self, articleid):
	self.update_state(state='PROCESSING', meta={'current': 5, 'total': 100, 'status': 'Downloading article...'})
	wp = wikipedia.page(articleid)
	content = wp.content
	self.update_state(state='PROCESSING', meta={'current': 10, 'total': 100, 'status': 'Processing article...'})
	words = content.split()
	replacecount = 0
	output = ""
	for i in range(0,len(words)):
		word = random.choice(words)
		if len(wn.synsets(word)) >= 1 and checkword(word):
			newword = wn.synsets(word)[0].lemma_names()[0]
			if not checksyn(newword):
				if len(wn.synsets(word)) >= 2:
					newword = wn.synsets(word)[1].lemma_names()[0]
					if not checksyn(newword):
						i -= 2
						continue
				else:
					i -= 2
					continue
			if newword == word:
				i -= 2
				continue
			else:
				content = content.replace(" " + word + " ", " " + newword + " ", 1)
				output += "Replaced " + word + " with " + newword + "\n"
				replacecount += 1
		else:
			i -= 2
		self.update_state(state='PROCESSING', meta={'current': i/100, 'total': 100, 'status': 'Editing article...'})
#		sleep(0.5)
	return {'current': 100, 'total': 100, 'status': 'Processing complete!', 'article': content, 'info': output}
	
	

def checkword(word):
	if len(word) < 5:
		return False
	if word[0].isupper():
		return False
	if word[-1] == 's':
		return False
	return True

def checksyn(word):
	if "_" in word:
		return False
	if word[0].isupper():
		return False
	return True


if __name__ == '__main__':
    app.run(host='0.0.0.0')
