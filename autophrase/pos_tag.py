import os
from glob import glob
from shutil import copyfile
from math import floor
import sys
import threading
# from download_parameter_files import download_parameter_files

def split_file(num_lines, num_files, raw, tmp):
	smallfile = None
	file_num = 0
	with open(raw) as bigfile:
		for lineno, line in enumerate(bigfile):
			if lineno % num_lines == 0 and file_num != num_files:
				if smallfile:
					smallfile.close()
				small_filename = tmp + "/split_files.{}".format(file_num)
				file_num += 1
				smallfile = open(small_filename, "w")
			smallfile.write(line)
		if smallfile:
			smallfile.close()

def one_line_per_word(file):
	with open(file) as input_file:
		with open(file + ".token", "w") as out_file:
			for line in input_file:
				out_file.write(line.replace(' ', '\n'))

def execute_tagger(file, tagger, parfile):
	command = tagger + " -quiet " + parfile + " < " + file + " > " + file + ".tagged"
	os.system(command)
	# with open(file) as token_file:
	# 	with open(file + ".tagged", 'w') as tagged:				
	# 		subprocess.call(command, stdin = token_file, stdout = tagged)


def pos_tag(language, num_thread, raw, tmp):
	root_path = os.path.dirname(os.path.abspath(__file__))
	# download_parameter_files(language, root_path)
	for file in glob(tmp + "/split_files*"):
		os.remove(file)

	print("Current step: Splitting files...")	
	with open(raw) as f:
		num_lines = floor(sum(1 for _ in f)/num_thread)
	if num_lines <= 0 or num_thread == 1:
		copyfile(raw, tmp + "/split_files.0")
	else:
		split_file(num_lines, num_thread, raw, tmp)

	for file in glob(tmp + "/split_files.*"):
		one_line_per_word(file)

	print("Current step: Tagging...")
	tagger = None
	parfile = None
	if language == "EN":
		tagger = root_path + "/tools/treetagger/bin/tree-tagger"
		parfile = root_path + "/tools/treetagger/lib/english-utf8.par"
	elif language == "FR":
		tagger = root_path + "/tools/treetagger/bin/tree-tagger"
		parfile = root_path + "/tools/treetagger/lib/french-utf8.par"
	elif language == "IT":
		tagger = root_path + "/tools/treetagger/bin/tree-tagger"
		parfile = root_path + "/tools/treetagger/lib/italian-utf8.par"
	elif language == "RU":
		tagger = root_path + "/tools/treetagger/bin/tree-tagger"
		parfile = root_path + "/tools/treetagger/lib/russian-utf8.par"
	elif language == "ES":
		tagger = root_path + "/tools/treetagger/bin/tree-tagger"
		parfile = root_path + "/tools/treetagger/lib/spanish-utf8.par"
	else:
		sys.exit("[ERROR]: Tree tagger does not support the language.")

	curent_directory = os.getcwd()
	# os.chdir(root_path + "/tools/treetagger")
	thread_list = []

	for file in glob(tmp + "/split_files.*.token"):
		t = threading.Thread(target = execute_tagger, args = (file, tagger, parfile,))
		thread_list.append(t)

	for thread in thread_list:
	    thread.start()

	for thread in thread_list:
		thread.join()

	# os.chdir(curent_directory)
	print("Current step: Merging...")

	with open(tmp + "/pos_tags.txt", "w") as outfile:
		for filenum in range(num_thread):
			file_name = tmp + "/split_files." + str(filenum) + ".token.tagged"
			with open(file_name, "r") as infile:
				outfile.write(infile.read())

	for file in glob(tmp + "/split_files*"):
		os.remove(file)