from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import soundfile as sf
import librosa
from typing import Tuple
import os
import torch

class AudioProcessor:
    CACHED_DIRECTORY = "cached_model"
    MODEL = "facebook/wav2vec2-large-960h"
    
    def __init__(self):
        """
        Cache the model and transformer into CACHED_DIRECTORY
        It will be useful for docker creation. In this case, we do not need to repeated download the model whenever we do `docker run`

        Basically, it will check
        """
        READ_PATH_OR_MODEL = self.__class__.CACHED_DIRECTORY
        NEED_SAVE = False
        if not os.path.exists(READ_PATH_OR_MODEL):
            READ_PATH_OR_MODEL = self.__class__.MODEL
            NEED_SAVE = True
        
        self.tokenizer = Wav2Vec2Processor.from_pretrained(READ_PATH_OR_MODEL)
        self.model = Wav2Vec2ForCTC.from_pretrained(READ_PATH_OR_MODEL)

        self.tokenizer.save_pretrained(self.__class__.CACHED_DIRECTORY)
        self.model.save_pretrained(self.__class__.CACHED_DIRECTORY)

        self.model_sample_rate = 16000 # This is based on the training samples' sample rate in model

        self.device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        
        self.model.to(self.device)

        print(f"Model is loaded on '{self.device}' device")
    
    def decode(self, audio_filepath: str) -> Tuple[str, float]:
        """
        Accepts an audio file path string and returns the transcripted text from the model

        Parameters:
        audio_filepath (str): audio file path string

        Returns:
        Tuple [str, float]: Transcripted String and Duration in float

        Example:
        >>> decode(filepath)
        ("ROAR THEY SAID", 2.5)
        """
        audio_input, sample_rate = sf.read(audio_filepath)
        if sample_rate != self.model_sample_rate:
            # Need to resample to same rate
            audio_input = librosa.resample(audio_input, orig_sr=sample_rate, target_sr=self.model_sample_rate)
        
        with torch.no_grad():
            # tokenise
            input_values = self.tokenizer(audio_input, sampling_rate=self.model_sample_rate, return_tensors="pt").input_values

            input_values = input_values.to(self.device)

            # retrieve logits
            logits = self.model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.tokenizer.decode(predicted_ids[0])

        return transcription, len(audio_input)/self.model_sample_rate

# import os

# from soundfile import _formats as audio_formats

# import datetime

# class AudioDownloadManager:
#     # Technically, we can make this thread group to reuse thread and allow multi threading download of the files.
#     # Will add if I have the time

#     def __init__(self, download_dir: str):
#         self.download_dir = download_dir

#         self.file_locations = {}
        
#         assert not os.path.exists(self.download_dir), f"Download dir exists: '{os.path.absname}'"
    
#     def download(self, f: werkzeug.datastructures.FileStorage) -> Tuple[str, str]:
#         """
#         Takes in file object and checks for correct audio types

#         Parameters:
#         f (werkzeug.datastructures.FileStorage): file to be downloaded to the server

#         Returns:
#         Tuple [str, str]: The final downloaded audio file path on the server and error message. 
#         Filepath would be empty if there is an error. If there is no error, error message will be empty.

#         """
#         f = request.files['file'] 

#         raw_basefile, raw_baseext = splitext(f.filename)
#         if raw_baseext[1:].upper() not in audio_formats:
#             return '', f"Wrong audio format '{raw_baseext}'. Valid format are {audio_formats}"
        
#         download_path = os.path.join(self.download_dir, f.filename)

#         if os.path.exists(download_path):
#             # Use another filename with timestamp suffix-ed
#             # Should be sufficient to handle the case
#             new_filename = f"{raw_basefile}_{int(datetime.datetime.now().timestamp())}{raw_baseext}"
#             download_path = os.path.join(self.download_dir, new_filename)
        
#         f.save(download_path)

#         if not os.path.exists(download_path): # Download fail for some reason
#             return '', f"Server is unable to download the file. Please try again later for '{f.filename}.'"
        
#         return download_path, ''