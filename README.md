
# MFA Formatter for Beginners
A simple tool to easily use Montreal Forced Aligner.

# Description
These days, as speech research community rapidly grows, text-wav forced alignment is necessary to the research such as Text-to-Speech, Voice Conversion and other speech-related search field. One simple and widely-used approach is to use Montreal Forced Aligner(MFA) [McAuliffe17] as text-wav forced aligner. Despite of lots of necessity, some speech-research beginners may feel that it is hard to train their custom dataset. For them, this repository offers following operations and procedures that are needed to run MFA with little efforts.
* Make whole dataset to [(wav, lab) pair-formatted structure](https://montreal-forced-aligner.readthedocs.io/en/latest/user_guide/corpus_structure.html#corpus-formats-and-structure) which is necessary to run MFA
* Generate phoneme dictionary from [pretranied G2P model](https://mfa-models.readthedocs.io/en/latest/g2p/English/English%20%28US%29%20ARPA%20G2P%20model%20v2_0_0.html#English%20(US)%20ARPA%20G2P%20model%20v2_0_0) provided from [official MFA documents](https://mfa-models.readthedocs.io/en/latest/g2p/index.html#g2p)
* Train MFA using pre-formatted (wav-lab) paired dataset and generated phoneme dictionary
* Validate and visualize the extracted TextGrid(alignment) via [jupyter notebook](https://github.com/Jackson-Kang/MFAFormatter/blob/main/visualize_alignment.ipynb)
* Provide the text-wav alignment from [Emotional Speech Dataset (ESD) [Zhou21]](https://arxiv.org/abs/2105.14762) 

# How to use
To run this program, please follow the procedure below.
* Install [anaconda](https://www.anaconda.com/) and python=3.9.
* [Install MFA](https://montreal-forced-aligner.readthedocs.io/en/latest/getting_started.html) and [download ESD dataset](https://github.com/HLTSingapore/Emotional-Speech-Data)
* Install pre-requisite modules using pip via following command
```pip install -r requirements.txt```
* Edit `config.py` to point your database.
* Run formatter 
```python main.py```

# Alignments
As a result of this tutorial, I upload text-wav alignment extracted using MFA.
*  [Emotional Speech Dataset (ESD) [Zhou21]](https://arxiv.org/abs/2105.14762) [[download](https://drive.google.com/file/d/11nCL1xUn8D133WHVzLFSB2rplHrXE8xM/view?usp=sharing)]

# Visualization of Extracted Alignments
Please refer [visualise_alignment.ipynb](https://github.com/Jackson-Kang/MFAFormatter/blob/main/visualize_alignment.ipynb).

# Supported Dataset
* [Emotional Speech Dataset (ESD) [Zhou21]](https://arxiv.org/abs/2105.14762) - a multispeaker-multiemotion dataset

# Experimental Notes
* currently, only supports ESD
* Since MFA use GMM, different emotions belonging to a single speaker were considered independently. (i.e., utterances with emotion 'Angry' from speaker A and utterances with emotion 'Sad' are treated with different speakers.)
* Please note that extracted alignments may not be accurate.
* Only English speakers are used.

# Contacts
Please email to mskang1478@gmail.com. Any suggestion or question be appreciated. 


