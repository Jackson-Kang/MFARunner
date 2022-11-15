from dataset import esd, kss, kes, emotiontts
from config import Arguments as args
from utils import create_dir

def run():

	dataset_path = args.dataset_path
	preprocessed_file_dir = args.preprocessed_file_dir
	result_dir = args.result_dir
	num_jobs = args.num_jobs
	phone_set = args.phone_set

	if "esd" in dataset_path.lower():
		instance = esd.EmotionalSpeechDataset(dataset_path, preprocessed_file_dir, result_dir, num_jobs=num_jobs, phone_set=phone_set)
	elif "kss" in dataset_path.lower():
		instance = kss.KoreanSingleSpeakerSpeechDataset(dataset_path, preprocessed_file_dir, result_dir, num_jobs=num_jobs, phone_set=None)	
	elif "korean_emotional_speech" in dataset_path.lower():
		instance = kes.KoreanEmotionalSpeechDataset(dataset_path, preprocessed_file_dir, result_dir, num_jobs=num_jobs, phone_set=None)
	elif "emotiontts" in dataset_path.lower():
		instance = emotiontts.EmotionTTSDataset(dataset_path, preprocessed_file_dir, result_dir, num_jobs=num_jobs, phone_set=None)
	else:
		print("[ERROR] No dataset named {}.".format(dataset_name.split("/")[-1]))
		return


	instance.run()
	




if __name__ =="__main__":

	run()
