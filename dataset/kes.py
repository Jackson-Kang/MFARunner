from utils import do_multiprocessing, get_filelist, copy_file, read_meta, write_meta, create_dir, run_mfa
from utils import get_korean_dictionary, remove_special_symbols

import os, itertools, sys, ffmpeg
from g2pk import G2p

g2p = G2p()

class KoreanEmotionalSpeechDataset():

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
		raw_filepath, transcript, save_dir  = info

		filename = raw_filepath.split("/")[-1].replace(".raw", "")

		save_lab_filepath = os.path.join(save_dir, filename + ".lab")
		save_wav_filepath = os.path.join(save_dir, filename + ".wav")


		if not os.path.exists(save_wav_filepath):
			try:
				out, err = (ffmpeg
						.input(raw_filepath, format='s16le', ar=16000)
						.output(save_wav_filepath, ac=1, codec='pcm_s16le', ar=16000)
						.overwrite_output()
						.run(capture_stdout=True, capture_stderr=True))

			except ffmpeg.Error as err:
				print(err.stderr, file=sys.stderr)
				raise

		write_meta(transcript, save_lab_filepath)


	def run(self):

		raw_filepaths = get_filelist(os.path.join(self.dataset_path, "**", "**"), file_format="raw")	
		raw_filepaths = [(raw_filepath.split("/")[-1], raw_filepath) for raw_filepath in raw_filepaths]
		raw_filepaths.sort(key=lambda x: x[0])
		_, raw_filepaths = list(zip(*raw_filepaths))


		save_dirs = [os.path.join(self.preprocessed_file_dir, raw_filepath.split("/")[-3].strip("_3000_16000Hz").strip("_3000_16000HZ_2018")) 
													for raw_filepath in raw_filepaths] 
		save_dirs = [create_dir(save_dir) for save_dir in save_dirs]


		transcripts = [read_meta(raw_filepath.replace("raw", "txt"))[0] for raw_filepath in raw_filepaths]
		transcripts = remove_special_symbols(transcripts)

		file_infos = list(zip(raw_filepaths, transcripts, save_dirs))
		do_multiprocessing(job=self.job, tasklist=file_infos, num_jobs=self.num_jobs)	

		dictionary = get_korean_dictionary(transcripts, g2p)

		dictionary_path = os.path.join(self.result_dir, "{}_dictionary.txt".format(self.dataset_name))
		textgrid_path = os.path.join(self.result_dir, "TextGrid")

		write_meta(dictionary, dictionary_path)

		run_mfa(self.preprocessed_file_dir+"/", dictionary_path, textgrid_path, num_jobs=self.num_jobs, phone_set=self.phone_set)

