import os
import shutil

class Autophrase:
    def __init__(self):
        self.HIGHLIGHT_MULTI = "0.8"
        self.HIGHLIGHT_SINGLE = "1.0"
        self.ENABLE_POS_TAGGING = 1
        self.THREAD = "10"
        self.model = "models/DBLP"
        self.tmp = "tmp"
        self.LANGUAGE = "UNKNOWN"
        self.TOKENIZER = "-cp .:tools/tokenizer/lib/*:tools/tokenizer/resources/:tools/tokenizer/build/ Tokenizer"
        
    def tokenize(self, filename):
        self.TEXT_TO_SEG = filename
        self.SEGMENTATION_MODEL = self.model + "/segmentation.model"
        TOKEN_MAPPING = self.model + "/token_mapping.txt"
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp)
        os.mkdir(self.tmp)
        print("===Tokenization===")
        TOKENIZED_TEXT_TO_SEG = self.tmp+"/tokenized_text_to_seg.txt"
        CASE = self.tmp + "/case_tokenized_text_to_seg.txt"
        os.system("time java " + self.TOKENIZER + " -m direct_test -i " + self.TEXT_TO_SEG + " -o " + TOKENIZED_TEXT_TO_SEG + " -t " + TOKEN_MAPPING + " -c N -thread " + self.THREAD)
        language_file = open(self.model+"/language.txt", 'r')
        self.LANGUAGE = language_file.read()
        language_file.close()
        print("Detected Language: " + self.LANGUAGE)

    def pos_tagging(self):
        if self.LANGUAGE != "JA"and self.LANGUAGE != "CN" and self.LANGUAGE != "OTHER" and self.ENABLE_POS_TAGGING == 1:
            RAW = self.tmp + "/raw_tokenized_text_to_seg.txt"
            os.environ["THREAD"] = self.THREAD
            os.environ["LANGUAGE"] = self.LANGUAGE
            os.environ["RAW"] = RAW
            os.system("bash tools/treetagger/pos_tag.sh")
            os.rename(self.tmp + "/pos_tags.txt", self.tmp + "/pos_tags_tokenized_text_to_seg.txt")

    def phrase_segmentation(self):
        print("===Phrasal Segmentation===")
        if self.ENABLE_POS_TAGGING == 1:
            command = "./bin/segphrase_segment --pos_tag" + \
                        " --thread " + self.THREAD + \
                        " --model " + self.SEGMENTATION_MODEL + \
                        " --highlight-multi " + self.HIGHLIGHT_MULTI + \
                        " --highlight-single " + self.HIGHLIGHT_SINGLE
        else:
            command = "./bin/segphrase_segment --pos_tag" + \
                        " --thread " + self.THREAD + \
                        " --model " + self.SEGMENTATION_MODEL + \
                        " --highlight-multi " + self.HIGHLIGHT_MULTI + \
                        " --highlight-single " + self.HIGHLIGHT_SINGLE
        os.system(command)

    def generate_output(self):
        print("===Generating Output===")
        os.system("java " + self.TOKENIZER + " -m segmentation -i " + self.TEXT_TO_SEG + " -segmented tmp/tokenized_segmented_sentences.txt -o " + self.model + "/segmentation.txt -tokenized_raw tmp/raw_tokenized_text_to_seg.txt -tokenized_id tmp/tokenized_text_to_seg.txt -c N")
