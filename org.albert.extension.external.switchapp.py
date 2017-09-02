#!/usr/bin/env python

import subprocess
import sys
import re
import os
import json

albert_op = os.environ.get('ALBERT_OP')

if albert_op == 'METADATA':
	metadata = """{
	"iid": "org.albert.extension.external/v2.0",
	"name": "WindowSwitcher",
	"version": "1.0",
	"author": "Klesh Wong",
	"dependencies": [],
	"trigger": "-"
	}"""
	print(metadata)
	sys.exit(0)
elif albert_op == 'QUERY':
	albert_query = os.environ.get('ALBERT_QUERY')

	if albert_query:
		albert_query = albert_query[1:]

	windowStr, error = subprocess.Popen(['wmctrl', '-lp'], stdout=subprocess.PIPE).communicate()

	patternPidAndName = re.compile(r'^(\w+)\s+(\d+)\s+(\d+)\s+(.+)$')
	patternProcessName = re.compile(r'^\s+\d+\s+[^\s]+\s+[^\s]+\s+(.+)$')

	items = []

	for line in windowStr.split('\n'):
		match = patternPidAndName.match(line)

		if not match:
			continue

		wid = match.group(1)
		pid = match.group(3)
		name = match.group(4)

		pidStr, error = subprocess.Popen(['ps', '-p', pid, '--no-headers'], stdout=subprocess.PIPE).communicate()

		if error:
			sys.exit(1)

		match = patternProcessName.match(pidStr)

		if match:
			name = match.group(1) + ' - ' + name

			if albert_query and albert_query.lower() not in name.lower():
				continue

			item = {
			 'id' : wid,
			 'name' : name,
			 'actions' : [{
				 'name': 'Activate',
				 'command': 'python',
				 'arguments': [
					 __file__,
					 str(wid)
				 ]
			 }]
			}

			items.append(item)

	resp = {
		'items' : items
	}

	print(json.dumps(resp))


if len(sys.argv) > 1:
	window_id = sys.argv[1]
	subprocess.Popen(['wmctrl', '-ia', window_id])
