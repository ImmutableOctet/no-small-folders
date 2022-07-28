import sys
import os
import os.path
import errno
import shutil
import argparse

def ensure_path(path):
	if not os.path.exists(os.path.dirname(path)):
		try:
			os.makedirs(os.path.dirname(path))
		except OSError as exc:
			if (exc.errno != errno.EEXIST):
				raise

def is_empty_folder(path):
	return (len(os.listdir(path)) == 0)

def remove_empty_dirs(root_path):
	for (path, dir_names, file_names) in os.walk(root_path, topdown=False):
		if ((len(dir_names) == 0) and (len(file_names) == 0)):
			print(f'Removing empty directory: "{path}"')

			os.rmdir(path) # os.remove(path)


# Code by nosklo on StackOverflow:
# https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
def walk_level(some_dir, level=1, topdown=True):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir, topdown=topdown):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

def no_small_folders(cfg, ignore_parent_folders=True):
	ensure_path(cfg.output_path)

	for (path, dir_names, file_names) in walk_level(cfg.input_path, cfg.recursion_depth): # os.walk(cfg.input_path): # topdown=False
		#print(f'@ "{path}"')
		
		subfolder_count = len(dir_names)

		if ((ignore_parent_folders) and (subfolder_count > 0)):
			continue
		
		file_count = len(file_names)

		if (file_count >= cfg.size_threshold):
			continue
		
		if (file_count > 0):
			print(f'Small folder found @ "{path}" [Files: {file_count}]:')

			# List of files as a string.
			file_list_rep = ', '.join([f'"{f}"' for f in file_names])

			print(f'{file_list_rep} -> "{cfg.output_path}"')

			for file_name in file_names:
				full_file_path_in = os.path.join(path, file_name)
				full_file_path_out = os.path.join(cfg.output_path, file_name)

				# Check if a file already exists at the target location.
				if (os.path.isfile(full_file_path_out)):
					current_dir_name = os.path.basename(path) # os.path.dirname(path)
					new_file_name = f'{current_dir_name} - {file_name}'
					full_file_path_out = os.path.join(cfg.output_path, new_file_name)

					assert (not os.path.isfile(full_file_path_out))

				shutil.move(full_file_path_in, full_file_path_out)
		
		#if (is_empty_folder(path)):
		#	...	

	if (cfg.remove_empty_folders):
		remove_empty_dirs(cfg.input_path)

def main(argv):
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='Move the contents of folders with a low number of files in them. (e.g. 1 file per-folder)\n')

	parser.add_argument('-i', "--input", dest='input_path', required=True)
	parser.add_argument('-o', "--output", dest='output_path', required=True)

	parser.add_argument('-st', "--size-threshold", dest='size_threshold', default=3)
	#parser.add_argument('-ip', "--ignore-parent-folders", dest='ignore_parent_folders', default=True)

	parser.add_argument('-r', "--recursion-depth", dest='recursion_depth', default=1)
	parser.add_argument('-c', "--clean", dest='remove_empty_folders', default=True, action='store_true')

	cfg = parser.parse_args(argv)

	no_small_folders(cfg)


if __name__ == "__main__":
	#main(['-i', 'E:\\Downloads\\New folder', '-o', 'E:\\Downloads\\Test'])
	
	main(sys.argv[1:])