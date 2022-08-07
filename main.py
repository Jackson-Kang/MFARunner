from dataset import esd
from config import Arguments as args
from utils import create_dir

def run():

	dataset_path = args.dataset_path
	preprocessed_file_dir = args.preprocessed_file_dir

	if "esd" in dataset_path.lower():
		instance = esd.EmotionalSpeechDataset(dataset_path, preprocessed_file_dir)
	else:
		print("[ERROR] No dataset named {}.".format(dataset_name.split("/")[-1]))
		return


	instance.run()
	




if __name__ =="__main__":

	run()
