
# adjust configuration



class Arguments:
	
	#dataset_path = "/home/minsu/hdd1/dataset/speech/korean/emotiontts_open_db"
	#dataset_path = "/home/minsu/hdd1/dataset/speech/korean/korean_emotional_speech"
	dataset_path = "/home/minsu/hdd1/dataset/speech/korean/kss"

	preprocessed_file_dir = "./preprocessed"	

	result_dir = "./result"
	phone_set = None 		# if use pretrained model, set phone_set to 'english_us_arpa' or etcs..

	num_jobs=8
