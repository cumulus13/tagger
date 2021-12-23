#!/usr/bin/env python

from __future__ import print_function

import re
from mutagen.id3 import ID3
import os, sys
from pydebugger.debug import debug
from make_colors import make_colors
from unidecode import unidecode

if os.path.isdir(sys.argv[1]):
	files = [os.path.join(os.path.realpath(sys.argv[1]), i.split("\n")[0]) for i in os.listdir(sys.argv[1])]
	debug(files = files)
	files = list(filter(None, files))
	debug(files = files)
	files = list(filter(lambda k: k.lower().endswith("mp3"), files))
	debug(files = files)
elif os.path.isfile(sys.argv[1]):
	files = [os.path.realpath(sys.argv[1]).split("\n")[0]]
	debug(files = files)
	files = list(filter(None, files))
	debug(files = files)

for i in files:
	a = ID3(i)
	for k in a.keys():
		if hasattr(a[k], "text"):
			print(
				make_colors(str(k) + ":", "lb") + " " +\
				make_colors(a[k].text, 'y')
			)
			print(("type(a[k].text):", type(a[k].text)))
			if isinstance(a[k].text, list):
				if "pmedia" in str(a[k].text).lower():
					if "www" in str(a[k].text).lower():
						new_text = "licface@yahoo.com"
					else:
						new_text = "LICFACE"
					a[k].text = [new_text]
			elif "pmedia" in str(a[k].text.encode('utf-8')).lower():
				if "www" in str(a[k].text).lower():
					new_text = "licface@yahoo.com"
				else:
					new_text = "LICFACE"
				a[k].text = new_text
		elif hasattr(a[k], "url"):
			print(
				make_colors(str(k) + ":", "lg") + " " +\
				make_colors(a[k].url, 'lm')
			)
			if "pmedia" in str(a[k].url).lower():
				if "www" in str(a[k].url).lower():
					new_text = "licface@yahoo.com"
				else:
					new_text = "LICFACE"
				a[k].url = new_text
	a.save()
	print("-"*100)
