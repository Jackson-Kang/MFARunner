from multiprocessing import Pool
from tqdm import tqdm
from glob import glob

import os, chardet

def copy_file(source_file, dest_file):
	os.system("cp {} {}".format(source_file, dest_file))

def get_filelist(dirname, file_format):
	filepath = os.path.join(dirname, "*.{}".format(file_format))
	return list(glob(filepath))

def do_multiprocessing(job, tasklist, num_jobs=8):
	p = Pool(num_jobs)
	with tqdm(total=len(tasklist)) as pbar:
		for _ in tqdm(p.imap_unordered(job, tasklist)):
			pbar.update()	

def get_path(*args):
	return os.path.join('', *args)

def create_dir(*args):
        path = get_path(*args)
        if not os.path.exists(path):
                os.mkdir(path)
        return path

def read_meta(path):
	try: 
		with open(path, 'r', encoding='utf-8') as f:
			lines = f.readlines()
	except:
		rawdata = open(path, "rb").read()
		detected_encoding = chardet.detect(rawdata)

		with open(path, 'r', encoding=detected_encoding['encoding']) as f:
			lines = f.readlines()
	lines = [line.lstrip().rstrip() for line in lines if line not in ["\n", "\t", " ", "\t\n"]]

	return lines


def write_meta(transcripts, savepath):

	"""
		Args:
			transcripts:	[list]   list of transcript
			savepath:	[string] path to store metadata
	"""


	with open(savepath, 'w') as f:
		f.writelines(transcripts)

def run_mfa(wav_lab_path, dict_path, save_textgrid_path, use_pretrained_g2p=True):
	if use_pretrained_g2p:
		print("\n[LOG] start to generate dictionary..")
		os.system("mfa g2p  english_us_arpa {} {}".format(wav_lab_path, dict_path))

	print("\n[LOG] validate (wav, lab) format and generated dictionary..")
	os.system("mfa validate {} {}".format(wav_lab_path, dict_path))		# validate wavlab and generated dictionary

	print("\n[LOG] start train forced aligner..")
	os.system("mfa train {} {} {}".format(wav_lab_path, dict_path, save_textgrid_path))


