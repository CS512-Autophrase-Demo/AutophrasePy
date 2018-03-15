import os
import shutil

class Autophrase:
    def __init__(self):
        self.HIGHLIGHT_MULTI = 0.8
        self.HIGHLIGHT_SINGLE = 1.0
        self.ENABLE_POS_TAGGING = 1
        self.THREAD = "10"
        self.model = "models/HW1/DBLP"
        self.tmp = "./ttmp"
    def phrasalseg(self, filename):
        TEXT_TO_SEG=filename
        SEGMENTATION_MODEL=self.model+"/segmentation.model"
        TOKEN_MAPPING=self.model+"/token_mapping.txt"
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp)
        os.mkdir(self.tmp)
        print("===Tokenization===")
        TOKENIZER="-cp .:tools/tokenizer/lib/*:tools/tokenizer/resources/:tools/tokenizer/build/ Tokenizer"
        TOKENIZED_TEXT_TO_SEG=self.tmp+"/tokenized_text_to_seg.txt"
        CASE=self.tmp+"/case_tokenized_text_to_seg.txt"
        os.system("time java "+TOKENIZER+" -m direct_test -i "+TEXT_TO_SEG+" -o "+TOKENIZED_TEXT_TO_SEG+" -t "+TOKEN_MAPPING+" -c N -thread "+self.THREAD)
        output = os.popen("cat "+self.model+"/language.txt")
        print(output.read())