#!/bin/sh
celery worker -A main.celery --loglevel=info
