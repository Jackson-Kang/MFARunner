from multiprocessing import Pool
from tqdm import tqdm
from glob import glob
from jamo import hangul_to_jamo

import matplotlib
matplotlib.use('pdf')

import matplotlib.pyplot as plt
import numpy as np
import os, chardet
import tgt, re
from konlpy.tag import Mecab

mecab = Mecab()

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

def read_meta(path, encoding='utf-8'):
	try: 
		with open(path, 'r', encoding=encoding) as f:
			lines = f.readlines()
	except:
		rawdata = open(path, "rb").read()
		detected_encoding = chardet.detect(rawdata)

		with open(path, 'r', encoding=detected_encoding['encoding']) as f:
			lines = f.readlines()
	lines = [line.lstrip().rstrip() for line in lines if line not in ["\n", "\t", " ", "\t\n"]]

	return lines

def remove_special_symbols(transcripts):

	transcripts = "@".join(transcripts)
	transcripts = re.sub("[$!#,.\"\'?;:~<>]", "", transcripts)
	return transcripts.split("@")


def get_korean_dictionary(transcripts, g2p):

	pronunciation_dict = []

	print("[LOG] Generate dictionary..")
	for transcript in tqdm(transcripts, total=len(transcripts)):
		word_list = transcript.rstrip().split(" ")
		word_p_list = g2p(transcript.rstrip()).split(" ")

		for word, word_p in list(zip(word_list, word_p_list)):
			word_p = " ".join(list(hangul_to_jamo(word_p)))
			line = "{}\t{}\n".format(word, word_p)
			if word not in pronunciation_dict:
				pronunciation_dict.append(line)

	return pronunciation_dict



def write_meta(transcripts, savepath):

	"""
		Args:
			transcripts:	[list]   list of transcript
			savepath:	[string] path to store metadata
	"""

	with open(savepath, 'w') as f:
		f.writelines(transcripts)

def run_mfa(wav_lab_path, dict_path, save_textgrid_path, phone_set=None, num_jobs=8):

	os.system("mfa configure --always_clean --disable_textgrid_cleanup --j {}".format(num_jobs))

	if phone_set:
		print("\n[LOG] start to generate dictionary..")
		os.system("mfa g2p  {} {} {} --j {}".format(phone_set, wav_lab_path, dict_path, num_jobs))


	print("\n[LOG] validate (wav, lab) format and generated dictionary..")
	os.system("mfa validate {} {} --j {}".format(wav_lab_path, dict_path, num_jobs))		# validate wavlab and generated dictionary

	print("\n[LOG] start train forced aligner..")
	os.system("mfa train {} {} {} --j {}".format(wav_lab_path, dict_path, save_textgrid_path, num_jobs))



def plot_text_mel_alignment(mel, segmentation_boundary, text_sequence):
	fig, axis = plt.subplots()
	n_mels = mel.shape[0]

	axis.imshow(mel, origin='lower')
	axis.set_aspect(2.5, adjustable='box')

	axis.set_ylabel('n_mels')
	axis.set_ylim(0, n_mels)
	axis.set_yticks(np.arange(n_mels))

	axis.set_xlabel("time")
	axis.tick_params(labelsize='x-small', left=False, labelleft=False)
	axis.set_anchor('W')

	axis.vlines(segmentation_boundary, 0, n_mels, colors='r', linestyle='dashed', linewidth=0.5)

	for idx, segment_label in enumerate(segmentation_boundary):
		plt.text(segment_label, n_mels//2, "{}".format(text_sequence[idx]), color='r', fontsize=10)



def get_duration_from_textgrid(textgrid_path, sil_phones=['sil', "sp", "spn", ""], sampling_rate=16000, hop_length=256):

	"""
		from ming024's FastSpeech2 implementation
		
		ref)
			https://github.com/ming024/FastSpeech2/blob/7011fa1b86239a49a9154a5fcea45474c947acb1/preprocessor/preprocessor.py#L253
	"""

	textgrid = tgt.io.read_textgrid(textgrid_path)
	tier = textgrid.get_tier_by_name("phones")
         
	phones, durations = [], []
	start_time, end_time, end_idx = 0, 0, 0
        
	for idx, t in enumerate(tier._objects):
		s, e, p = t.start_time, t.end_time, t.text
            
		# Trim leading silences
		if phones == []:
			if p in sil_phones:
				continue
			else:
				start_time = s

		if p not in sil_phones:
			# For ordinary phones
			phones.append(p)
			end_time = e
			end_idx = len(phones)
            
		else:
			# For silent phones
			phones.append(p)

		durations.append(
			int(
				np.round(e * sampling_rate / hop_length)
					- np.round(s * sampling_rate / hop_length)))

        # Trim tailing silences
	phones = phones[:end_idx]
	durations = durations[:end_idx]

	start_time = int(sampling_rate * start_time)
	end_time = int(sampling_rate * end_time)

	if len(phones) != len(durations):
		print("[WARNING] phone length {} vs. duration length does not match!".format(len(phones), len(durations)))

	return phones, durations, start_time, end_time

