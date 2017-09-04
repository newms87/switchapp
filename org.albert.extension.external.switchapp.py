#!/usr/bin/env python

import sys
import os
import json
import commands
from ConfigParser import SafeConfigParser


"""
A window switcher that opens existing applications
requires: wmctrl
"""


albert_op = os.environ.get('ALBERT_OP')

APP_DIR = "/usr/share/applications/"
LOCAL_APP_DIR = os.path.expanduser("~/.local/share/applications/")

if albert_op == 'METADATA':
	metadata = """{
	"iid": "org.albert.extension.external/v2.0",
	"name": "AppSwitch",
	"version": "1.0",
	"author": "Daniel Newman",
	"dependencies": [],
	"trigger": "-"
	}"""
	print(metadata)
	sys.exit(0)

elif albert_op == "NAME":
	print("AppSwitch")
	sys.exit(0)

elif albert_op == "INITIALIZE":
	if not commands.getstatusoutput("which wmctrl")[0] is 0:
		sys.exit(1)
	sys.exit(0)

elif albert_op == 'QUERY':
	def parse_config_file(program):
		config_file = ""
		parts = program.split('.')

		for part in parts:
			if os.path.exists(APP_DIR + part + ".desktop"):
				config_file = APP_DIR + part + ".desktop"
				break

			if os.path.exists(LOCAL_APP_DIR + part + ".desktop"):
				config_file = LOCAL_APP_DIR + part + ".desktop"
				break

		if config_file == "":
			return ["",""]
		else:
			parser = SafeConfigParser()
			parser.read(config_file)
			return [parser.get("Desktop Entry","Name"), parser.get("Desktop Entry","Icon")]


	albert_query = "".join(os.environ.get("ALBERT_QUERY").split("-")[1:]).lower()

	window_list = commands.getoutput("wmctrl -lpx | awk '{printf $1\"|\"$3\"|\"$4\"|\"; $1=$2=$3=$4=$5=\"\"; gsub(/^ /,\"\",$0); print $0}'").split("\n")

	items = []

	for line in window_list:
		wid, pid, program, window_name = line.split('|')

		name, icon = parse_config_file(program)

		search_str = (name + " " + window_name).lower()

		if not name:
			name = window_name

		description = window_name

		if albert_query and albert_query not in search_str:
			continue

		item = {
			'id' : wid,
			'name' : name,
			'icon': icon,
			'description': description,
			'completion': 'switched',
			'actions' : [{
				'name': 'Activate',
				'command': 'wmctrl',
				'arguments': ["-ia",wid]
			}]
		}

		items.append(item)

	print(json.dumps({'items': items}))
	sys.exit(0)

elif albert_op in ["FINALIZE", "SETUPSESSION", "TEARDOWNSESSION"]:
	sys.exit(0)
