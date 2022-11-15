from utils import do_multiprocessing, get_filelist, copy_file, read_meta, write_meta, create_dir, run_mfa
from utils import get_korean_dictionary, remove_special_symbols

import os, itertools, sys
from g2pk import G2p

g2p = G2p()

class KoreanSingleSpeakerSpeechDataset():

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
		wav_filepath, transcript, save_dir = info

		filename =  wav_filepath.split("/")[-1]
		transcript_filename = transcript.split("|")[0]
		text = transcript.split("|")[2]

		if filename not in transcript_filename:
			print("[ERROR] transcript filename and wav-filename doesn't match!")
			print("\t\t transcript_filename: {} vs. wav-filename: {}".format(transcript_filename, filename))		
			sys.exit(0)
			return

		wav_savepath = os.path.join(save_dir, filename)
		transcript_savepath = os.path.join(save_dir, filename.replace(".wav", ".lab"))

		copy_file(wav_filepath, wav_savepath)		
		write_meta(text, transcript_savepath)

	def run(self):

		wav_filepaths = get_filelist(os.path.join(self.dataset_path, "**", "**"), file_format="wav")
		wav_filepaths = [(wav_filepath.split("/")[-1], wav_filepath) for wav_filepath in wav_filepaths]
		wav_filepaths.sort(key=lambda x: x[0])
		_, wav_filepaths = list(zip(*wav_filepaths))

		transcripts = read_meta(os.path.join(self.dataset_path, "transcript.v.1.4.txt"))

		if len(wav_filepaths) != len(transcripts):
			print("[ERROR] num of wavs and num of transcripts doesn't match! ({} vs. {})".format(len(wav_filepaths), len(transcripts)))
			return

		save_dirs = [self.preprocessed_file_dir for _ in range(len(transcripts))] 

		file_infos = list(zip(wav_filepaths, transcripts, save_dirs))
		do_multiprocessing(job=self.job, tasklist=file_infos, num_jobs=self.num_jobs)	

		transcripts = [transcript.split("|")[2] for transcript in transcripts]
		transcripts = remove_special_symbols(transcripts)
		dictionary = get_korean_dictionary(transcripts, g2p)

		dictionary_path = os.path.join(self.result_dir, "{}_dictionary.txt".format(self.dataset_name))
		textgrid_path = os.path.join(self.result_dir, "TextGrid")

		write_meta(dictionary, dictionary_path)

		run_mfa(self.preprocessed_file_dir+"/", dictionary_path, textgrid_path, num_jobs=self.num_jobs, phone_set=self.phone_set)

