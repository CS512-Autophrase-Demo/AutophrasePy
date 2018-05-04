import os
import shutil
from .pos_tag import pos_tag

class Autophrase:
    def __init__(self, highlight_multi=0.8, highlight_single=1.0, thread=10, pos_tagging=True):
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.curent_directory = os.getcwd()
        # self.installation_path = os.path.dirname(os.path.abspath(__file__))
        self.highlight_multi = str(highlight_multi)
        self.highlight_single = str(highlight_single)
        self.enable_pos_tagging = pos_tagging
        self.thread = str(thread)
        self.model = self.root_path + "/models/DBLP"
        self.segmentation_model = self.model + "/segmentation.model"
        self.tmp = self.curent_directory + "/tmp"
        tokenizer_path = self.root_path + ":" + self.root_path + "/tools/tokenizer/lib/*" + ":" + self.root_path + "/tools/tokenizer/resources/" + ":" + self.root_path + "/tools/tokenizer/build/"
        self.tokenizer = "-cp " + tokenizer_path + " Tokenizer"
    
    @staticmethod
    def phrasal_segment():
        a = Autophrase()
        a.tokenize("DBLP.5K.txt", "EN")
        a.pos_tagging()
        a.phrase_segmentation()
        a.generate_output()

    def tokenize(self, filename, language):
        self.text_to_seg = filename
        token_mapping = self.model + "/token_mapping.txt"
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp)
        os.mkdir(self.tmp)
        print("===Tokenization===")
        tokenized_text_to_seg = self.tmp + "/tokenized_text_to_seg.txt"
        CASE = self.tmp + "/case_tokenized_text_to_seg.txt"
        os.system("java " + self.tokenizer + " -m direct_test -i " + self.text_to_seg + " -o " + tokenized_text_to_seg + " -t " + token_mapping + " -c N -thread " + self.thread)
        #language_file = open(self.tmp + "/language.txt", 'r')
        self.language = language
        print("Detected Language: " + self.language)

    def pos_tagging(self):
        if self.language != "JA"and self.language != "CN" and self.language != "OTHER" and self.enable_pos_tagging == 1:
            RAW = self.tmp + "/raw_tokenized_text_to_seg.txt"            
            pos_tag("EN", int(self.thread), RAW, self.tmp)
            os.rename(self.tmp + "/pos_tags.txt", self.tmp + "/pos_tags_tokenized_text_to_seg.txt")

    def phrase_segmentation(self):
        print("===Phrasal Segmentation===")        
        #os.chdir(self.root_path)
        if self.enable_pos_tagging == 1:
            command = self.root_path + "/bin/segphrase_segment --pos_tag" + \
                        " --thread " + self.thread + \
                        " --model " + self.segmentation_model + \
                        " --text_to_seg_file " + self.tmp + "/tokenized_text_to_seg.txt" + \
                        " --text_seg_pos_tags_file " + self.tmp + "/pos_tags_tokenized_text_to_seg.txt" + \
                        " --output_tokenized_degmented_sentences " + self.tmp + "/tokenized_segmented_sentences.txt" + \
                        " --highlight-multi " + self.highlight_multi + \
                        " --highlight-single " + self.highlight_single
        else:
            command = self.root_path + "/bin/segphrase_segment" + \
                        " --thread " + self.thread + \
                        " --model " + self.segmentation_model + \
                        " --text_to_seg_file " + self.tmp + "/tokenized_text_to_seg.txt" + \
                        " --text_seg_pos_tags_file " + self.tmp + "/pos_tags_tokenized_text_to_seg.txt" + \
                        " --output_tokenized_degmented_sentences " + self.tmp + "/tokenized_segmented_sentences.txt" + \
                        " --highlight-multi " + self.highlight_multi + \
                        " --highlight-single " + self.highlight_single
        os.system(command)
        #os.chdir(self.curent_directory)

    def generate_output(self):
        print("===Generating Output===")
        command = "java " + self.tokenizer + " -m segmentation -i " + self.text_to_seg
        command = command + " -segmented " + self.tmp + "/tokenized_segmented_sentences.txt"
        command = command + " -o " + self.tmp + "/segmentation.txt"
        command = command + " -tokenized_raw " + self.tmp + "/raw_tokenized_text_to_seg.txt"
        command = command + " -tokenized_id " + self.tmp + "/tokenized_text_to_seg.txt -c N"
        os.system(command)
        #os.system("java " + self.tokenizer + " -m segmentation -i " + self.text_to_seg + " -segmented tmp/tokenized_segmented_sentences.txt -o " + self.model + "/segmentation.txt -tokenized_raw tmp/raw_tokenized_text_to_seg.txt -tokenized_id tmp/tokenized_text_to_seg.txt -c N")
