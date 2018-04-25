import os
import shutil
from pos_tag import pos_tag

class Autophrase:
    def __init__(self):
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.curent_directory = os.getcwd()
        self.installation_path = os.path.dirname(os.path.abspath(__file__))
        self.HIGHLIGHT_MULTI = "0.8"
        self.HIGHLIGHT_SINGLE = "1.0"
        self.ENABLE_POS_TAGGING = 1
        self.THREAD = "10"
        self.model = self.root_path + "/models/DBLP"
        self.SEGMENTATION_MODEL = self.model + "/segmentation.model"
        self.tmp = self.curent_directory + "/tmp"
        #self.LANGUAGE = "UNKNOWN"
        tokenizer_path = self.root_path + ":" + self.root_path + "/tools/tokenizer/lib/*" + ":" + self.root_path + "/tools/tokenizer/resources/" + ":" + self.root_path + "/tools/tokenizer/build/"
        self.TOKENIZER = "-cp " + tokenizer_path + " Tokenizer"
        
    def tokenize(self, filename, language):
        self.TEXT_TO_SEG = filename
        TOKEN_MAPPING = self.model + "/token_mapping.txt"
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp)
        os.mkdir(self.tmp)
        print("===Tokenization===")
        TOKENIZED_TEXT_TO_SEG = self.tmp + "/tokenized_text_to_seg.txt"
        CASE = self.tmp + "/case_tokenized_text_to_seg.txt"
        os.system("java " + self.TOKENIZER + " -m direct_test -i " + self.TEXT_TO_SEG + " -o " + TOKENIZED_TEXT_TO_SEG + " -t " + TOKEN_MAPPING + " -c N -thread " + self.THREAD)
        #language_file = open(self.tmp + "/language.txt", 'r')
        self.LANGUAGE = language
        print("Detected Language: " + self.LANGUAGE)

    def pos_tagging(self):
        if self.LANGUAGE != "JA"and self.LANGUAGE != "CN" and self.LANGUAGE != "OTHER" and self.ENABLE_POS_TAGGING == 1:
            RAW = self.tmp + "/raw_tokenized_text_to_seg.txt"            
            pos_tag("EN", int(self.THREAD), RAW, self.tmp)
            os.rename(self.tmp + "/pos_tags.txt", self.tmp + "/pos_tags_tokenized_text_to_seg.txt")

    def phrase_segmentation(self):
        print("===Phrasal Segmentation===")        
        #os.chdir(self.root_path)
        if self.ENABLE_POS_TAGGING == 1:
            command = self.root_path + "/bin/segphrase_segment --pos_tag" + \
                        " --thread " + self.THREAD + \
                        " --model " + self.SEGMENTATION_MODEL + \
                        " --text_to_seg_file " + self.tmp + "/tokenized_text_to_seg.txt" + \
                        " --text_seg_pos_tags_file " + self.tmp + "/pos_tags_tokenized_text_to_seg.txt" + \
                        " --output_tokenized_degmented_sentences " + self.tmp + "/tokenized_segmented_sentences.txt" + \
                        " --highlight-multi " + self.HIGHLIGHT_MULTI + \
                        " --highlight-single " + self.HIGHLIGHT_SINGLE
        else:
            command = self.root_path + "/bin/segphrase_segment --pos_tag" + \
                        " --thread " + self.THREAD + \
                        " --model " + self.SEGMENTATION_MODEL + \
                        " --highlight-multi " + self.HIGHLIGHT_MULTI + \
                        " --highlight-single " + self.HIGHLIGHT_SINGLE
        os.system(command)
        #os.chdir(self.curent_directory)

    def generate_output(self):
        print("===Generating Output===")
        command = "java " + self.TOKENIZER + " -m segmentation -i " + self.TEXT_TO_SEG
        command = command + " -segmented " + self.tmp + "/tokenized_segmented_sentences.txt"
        command = command + " -o " + self.tmp + "/segmentation.txt"
        command = command + " -tokenized_raw " + self.tmp + "/raw_tokenized_text_to_seg.txt"
        command = command + " -tokenized_id " + self.tmp + "/tokenized_text_to_seg.txt -c N"
        os.system(command)
        #os.system("java " + self.TOKENIZER + " -m segmentation -i " + self.TEXT_TO_SEG + " -segmented tmp/tokenized_segmented_sentences.txt -o " + self.model + "/segmentation.txt -tokenized_raw tmp/raw_tokenized_text_to_seg.txt -tokenized_id tmp/tokenized_text_to_seg.txt -c N")

a = Autophrase()
a.tokenize("DBLP_full.txt", "EN")
#a.LANGUAGE = "EN"
a.pos_tagging()
a.phrase_segmentation()
#a.TEXT_TO_SEG = "data/DBLP_full.txt"
a.generate_output()
