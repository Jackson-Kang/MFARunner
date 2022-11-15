from utils import do_multiprocessing, get_filelist, copy_file, read_meta, write_meta, create_dir, run_mfa
from utils import get_korean_dictionary, remove_special_symbols

import os, itertools, sys, ffmpeg
from g2pk import G2p

g2p = G2p()

class EmotionTTSDataset():

	"""
		only multispeaker-multiemotion dataset used
	"""


	def __init__(self, dataset_path, preprocessed_file_dir, result_dir, language='korean', num_jobs=8, phone_set=None):

		self.result_dir = result_dir
		self.dataset_path = dataset_path
		self.dataset_name = dataset_path.split("/")[-1]
		self.preprocessed_file_dir = preprocessed_file_dir
		self.phone_set = phone_set
		self.num_jobs = num_jobs

		create_dir(self.result_dir)
		create_dir(self.preprocessed_file_dir)

		self.preprocessed_file_dir = create_dir(os.path.join(preprocessed_file_dir, self.dataset_name))
		self.result_dir = create_dir(os.path.join(result_dir, self.dataset_name))


	def job(self, info):
		wav_filepath, transcript, save_dir  = info

		filename = wav_filepath.split("/")[-1].strip(".wav")

		save_lab_filepath = os.path.join(save_dir, filename + ".lab")
		save_wav_filepath = os.path.join(save_dir, filename + ".wav")

		copy_file(wav_filepath, save_wav_filepath)		
		write_meta(transcript, save_lab_filepath)


	def run(self):

		filters = ['plain-to-emotional', 'emotional-to-emotional']

		wav_filepaths = get_filelist(os.path.join(self.dataset_path, "**", "**", "wav"), file_format="wav")	
		wav_filepaths = [wav_filepath for wav_filepath in wav_filepaths if wav_filepath.split("/")[-4] in filters]

		wav_filepaths = [(wav_filepath.split("/")[-1], wav_filepath) for wav_filepath in wav_filepaths]
		wav_filepaths.sort(key=lambda x: x[0])
		_, wav_filepaths = list(zip(*wav_filepaths))


		save_dirs = self.filepath_to_savedir(wav_filepaths, self.preprocessed_file_dir)
		save_dirs = [create_dir(save_dir) for save_dir in save_dirs]

		transcript_filepaths = [wav_filepath.replace(".wav", ".txt").replace("wav", "transcript") for wav_filepath in wav_filepaths]
		transcripts = [read_meta(transcript_filepath, encoding='utf-8-sig')[0] for transcript_filepath in transcript_filepaths]
		transcripts = remove_special_symbols(transcripts)

		file_infos = list(zip(wav_filepaths, transcripts, save_dirs))
		do_multiprocessing(job=self.job, tasklist=file_infos, num_jobs=self.num_jobs)	

		dictionary = get_korean_dictionary(transcripts, g2p)

		dictionary_path = os.path.join(self.result_dir, "{}_dictionary.txt".format(self.dataset_name))
		textgrid_path = os.path.join(self.result_dir, "TextGrid")

		write_meta(dictionary, dictionary_path)

		run_mfa(self.preprocessed_file_dir+"/", dictionary_path, textgrid_path, num_jobs=self.num_jobs, phone_set=self.phone_set)

	def filepath_to_savedir(self, wav_filepaths, preprocessed_file_dir):
		
		save_dirs = []

		for idx in range(len(wav_filepaths)):
			wav_filepath = wav_filepaths[idx]
			save_dir = os.path.join(preprocessed_file_dir, wav_filepath.split("/")[-3])

			filename = wav_filepath.split("/")[-1].replace(".wav", "")
			file_index = int(filename[3:])

			if file_index >= 1 and file_index <= 100:
				save_dir += "_neu"
			elif file_index >= 101 and file_index <= 200:
				save_dir += "_hap"
			elif file_index >= 201 and file_index <= 300:
				save_dir += "_sad"
			else:
				save_dir += "_ang"
			save_dirs.append(save_dir)

		return save_dirs
