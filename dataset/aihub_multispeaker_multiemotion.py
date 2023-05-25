from utils import do_multiprocessing, get_filelist, copy_file, read_meta, write_meta, create_dir, run_mfa
from utils import get_korean_dictionary, remove_special_symbols

import os, itertools, sys
from g2pk import G2p

g2p = G2p()


class AIHubMSMEDataset():

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

		transcript, save_dirpath = info
		wav_filepath, grapheme_seq, _ = transcript	

		filename = wav_filepath.split("/")[-1]

		transcript_savepath = os.path.join(save_dirpath, filename.replace(".wav", ".lab"))
		wav_savepath = os.path.join(save_dirpath, filename)

		grapheme_seq = remove_special_symbols([grapheme_seq])[0]

		copy_file(wav_filepath, wav_savepath)		
		write_meta(grapheme_seq, transcript_savepath)


	def run(self):

		wav_filepaths = get_filelist(os.path.join(self.dataset_path, "**", "**"), file_format="wav")
		transcripts = read_meta(os.path.join(self.dataset_path, "metadata.csv"))
		transcripts = [transcript.split("|")[:3] for transcript in transcripts]

		save_dirs = [create_dir(os.path.join(self.preprocessed_file_dir, wav_filename.split("/")[0])) for (wav_filename, _, _) in transcripts] 
		transcripts = [[os.path.join(self.dataset_path, "wavs", wav_filename+'.wav'), grapheme, phoneme] 
							for (wav_filename, grapheme, phoneme) in transcripts]
		
		file_infos = list(zip(transcripts, save_dirs))
		do_multiprocessing(job=self.job, tasklist=file_infos, num_jobs=self.num_jobs)	

		transcripts = [transcript[1] for transcript in transcripts]
		dictionary = get_korean_dictionary(transcripts, g2p)

		dictionary_path = os.path.join(self.result_dir, "{}_dictionary.txt".format(self.dataset_name))
		textgrid_path = os.path.join(self.result_dir, "TextGrid")

		write_meta(dictionary, dictionary_path)

		run_mfa(self.preprocessed_file_dir+"/", dictionary_path, textgrid_path, num_jobs=self.num_jobs, phone_set=self.phone_set)

