import os
import sys
import shutil
import urllib.request
from .pos_tag import pos_tag
from .wiki_url import *

class Autophrase:
    def __init__(self, raw_train=None, filename=None, model_path=None, pretrained_model=None, language="EN", pos_tagging=True, highlight_multi=0.5, highlight_single=0.8, thread=10, min_sup=10):
        assert (raw_train is not None or filename is not None), "Either training file or segmenting file must be specified!"
        valid_language = ["EN", "CN", "JA", "ES", "AR", "FR", "IT", "RU"]
        assert (language in valid_language), "Invalid language! Only support EN, CN, JA, ES, AR, FR, IT, RU!"
        assert (0 <= highlight_multi and highlight_multi <= 1), "highlight_multi must be between 0 and 1!"
        assert (0 <= highlight_single and highlight_single <= 1), "highlight_single must be between 0 and 1!"
        assert (0 <= highlight_single and highlight_single <= 1), "highlight_single must be between 0 and 1!"
        assert (thread > 0), "thread must be greater than 0!"

        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.curent_directory = os.getcwd()

        self.raw_train = raw_train
        self.text_to_seg = filename
        self.language = language
        self.highlight_multi = str(highlight_multi)
        self.highlight_single = str(highlight_single)
        self.enable_pos_tagging = pos_tagging
        self.thread = str(thread)
        self.min_sup = str(min_sup)
        
        self.autophrase_folder = self.curent_directory + "/autophrase"
        self.tmp = self.autophrase_folder + "/tmp"
        self.model = self.autophrase_folder + "/models"        

        self.makedir(self.autophrase_folder)
        self.removedir(self.tmp)
        self.makedir(self.tmp)
        self.makedir(self.model)

        if self.language == "AR":
            self.tagger_model = self.root_path + "/tools/models/arabic.tagger"

        #TODO: set segmentation_model as a parameter, can copy it to models folder
        if raw_train is None: # segmentation
            self.build_segmentation_model(model_path, pretrained_model)            
        else:            
            self.download_wiki_files(self.language)
                
        tokenizer_path = self.root_path + ":" + self.root_path + "/tools/tokenizer/lib/*" + ":" + self.root_path + "/tools/tokenizer/resources/" + ":" + self.root_path + "/tools/tokenizer/build/"
        self.tokenizer = "-cp " + tokenizer_path + " Tokenizer"

    def removedir(self, dir):
        if os.path.exists(dir):
            try:
                shutil.rmtree(dir)
            except:
                print("Fail to remove folder "+ dir + " !")
                sys.exit()

    def makedir(self, dir):
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
            except:
                print("Fail to create folder "+ dir + " !")
                sys.exit()

    def download_wiki_files(self, language):
        self.data = self.autophrase_folder + "/data"
        self.makedir(self.data)
        self.data = self.data + "/" + self.language
        if not os.path.exists(self.data):
            self.makedir(self.data)
            urllib.request.urlretrieve(BAD_POS_TAGS, self.data + "/BAD_POS_TAGS.txt")
            if language == "EN":
                urllib.request.urlretrieve(EN_WIKI_ALL, self.data + "/wiki_all.txt")
                urllib.request.urlretrieve(EN_WIKI_QUALITY, self.data + "/wiki_quality.txt")
                urllib.request.urlretrieve(EN_STOPWORDS, self.data + "/stopwords.txt")
            elif language == "CN":
                urllib.request.urlretrieve(CN_WIKI_ALL, self.data + "/wiki_all.txt")
                urllib.request.urlretrieve(CN_WIKI_QUALITY, self.data + "/wiki_quality.txt")
                urllib.request.urlretrieve(CN_STOPWORDS, self.data + "/stopwords.txt")
            elif language == "JA":
                urllib.request.urlretrieve(JA_WIKI_ALL, self.data + "/wiki_all.txt")
                urllib.request.urlretrieve(JA_WIKI_QUALITY, self.data + "/wiki_quality.txt")
                urllib.request.urlretrieve(JA_STOPWORDS, self.data + "/stopwords.txt")
            elif language == "AR":
                urllib.request.urlretrieve(AR_WIKI_ALL, self.data + "/wiki_all.txt")
                urllib.request.urlretrieve(AR_WIKI_QUALITY, self.data + "/wiki_quality.txt")
                urllib.request.urlretrieve(AR_STOPWORDS, self.data + "/stopwords.txt")
            else:
                print("Currently we cannot support " + language)
                sys.exit()

    def build_segmentation_model(self, model_path, pretrained_model):
        self.segmentation_model = self.model + "/segmentation.model"
        if model_path is not None:
            try: 
                shutil.copy2(model_path, self.segmentation_model)
            except:
                print("Fail to copy segmentation model !")
                sys.exit()
        if not os.path.exists(self.segmentation_model):
            print("Downloading pretrained model ...")
            if self.language == "EN":
                if pretrained_model is None or pretrained_model == "DBLP":
                    urllib.request.urlretrieve(DBLP_MODEL, self.segmentation_model)
                elif pretrained_model == "YELP":
                    urllib.request.urlretrieve(YELP_MODEL, self.segmentation_model)
            elif self.language == "CN":
                urllib.request.urlretrieve(CN_MODEL, self.segmentation_model)
            elif self.language == "JA":
                urllib.request.urlretrieve(JA_MODEL, self.segmentation_model)
            elif self.language == "AR":
                urllib.request.urlretrieve(AR_MODEL, self.segmentation_model)
            else:
                print("You can not use pretrained model " + pretrained_model)
                sys.exit()
        if not os.path.exists(self.model + "/token_mapping.txt"):
            print("Downloading pretrained token mappings ...")
            if self.language == "EN":
                urllib.request.urlretrieve(EN_TOKENMAPPING, self.model + "/token_mapping.txt")
            elif self.language == "CN":
                urllib.request.urlretrieve(CN_TOKENMAPPING, self.model + "/token_mapping.txt")
            elif self.language == "JA":
                urllib.request.urlretrieve(JA_TOKENMAPPING, self.model + "/token_mapping.txt")
            elif self.language == "AR":
                urllib.request.urlretrieve(AR_TOKENMAPPING, self.model + "/token_mapping.txt")
            else:
                print("Currently we cannot support " + language)
                sys.exit()

    @staticmethod
    def train_model(trainfile=None, language="EN", pos_tagging=True, thread=10, min_sup=10):
        if not os.path.exists(trainfile):
            print("Training file not exists !")
            sys.exit()
        a = Autophrase(raw_train = trainfile, language=language, pos_tagging=pos_tagging, thread=thread, min_sup=min_sup)
        a.tokenize_training_file()
        a.tokenize_wiki_and_stopwords()
        a.pos_tagging_train()
        a.core_training()
        a.save_models()
        a.generate_output_training()

    def tokenize_training_file(self):
        print("===Tokenization===")
        print("Current step: Tokenizing training file...")
        tokenized_train = self.tmp + "/tokenized_train.txt"
        case = self.tmp + "/tokenized_train.txt"
        token_mapping = self.tmp + "/token_mapping.txt"

        command = "java " + self.tokenizer + " -m train -i " + self.raw_train + " -o " + tokenized_train + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)
        #self.language = open(self.tmp+"/language.txt", 'r').read().splitlines()[0]
        #print("Detected Language:", self.language)

    def tokenize_wiki_and_stopwords(self):
        tokenized_stopwords = self.tmp + "/tokenized_stopwords.txt"
        tokenized_all = self.tmp + "/tokenized_all.txt"
        tokenized_quality = self.tmp + "/tokenized_quality.txt"
        token_mapping = self.tmp + "/token_mapping.txt"

        stopwords = self.data + "/stopwords.txt"
        all_wiki_entities = self.data + "/wiki_all.txt"
        quality_wiki_entities = self.data + "/wiki_quality.txt"

        print("Current step: Tokenizing stopword file...")
        command = "java " + self.tokenizer + " -m test -i " + stopwords + " -o " + tokenized_stopwords + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)
        
        print("Current step: Tokenizing wikipedia phrases...")
        command = "java " + self.tokenizer + " -m test -i " + all_wiki_entities + " -o " + tokenized_all + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)
        command = "java " + self.tokenizer + " -m test -i " + quality_wiki_entities + " -o " + tokenized_quality + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)
    
    def pos_tagging_train(self):
        if self.language != "JA" and self.language != "CN" and self.language != "AR" and self.enable_pos_tagging == True:
            print("===Part-Of-Speech Tagging===")  
            raw = self.tmp + "/raw_tokenized_train.txt"            
            pos_tag(self.language, int(self.thread), raw, self.tmp)
            os.rename(self.tmp + "/pos_tags.txt", self.tmp + "/pos_tags_tokenized_train.txt")

    def core_training(self):
        print("===AutoPhrasing===")
        if self.enable_pos_tagging == 1:
            command = self.root_path + "/bin/segphrase_train --pos_tag" + \
                        " --train_file " + self.tmp + "/tokenized_train.txt" + \
                        " --train_capital_file " + self.tmp + "/case_tokenized_train.txt" + \
                        " --stopwords_file " + self.tmp + "/tokenized_stopwords.txt" + \
                        " --all_file " + self.tmp + "/tokenized_all.txt" + \
                        " --quality_file " + self.tmp + "/tokenized_quality.txt" + \
                        " --pos_tags_file " + self.tmp + "/pos_tags_tokenized_train.txt" + \
                        " --tmp " + self.tmp + \
                        " --thread " + self.thread + \
                        " --pos_prune " + self.data + "/BAD_POS_TAGS.txt" + \
                        " --label_method DPDN" + \
                        " --max_positives -1" + \
                        " --min_sup " + self.min_sup
        else:
            command = self.root_path + "/bin/segphrase_train" + \
                        " --train_file " + self.tmp + "/tokenized_train.txt" + \
                        " --train_capital_file " + self.tmp + "/case_tokenized_train.txt" + \
                        " --stopwords_file " + self.tmp + "/tokenized_stopwords.txt" + \
                        " --all_file " + self.tmp + "/tokenized_all.txt" + \
                        " --quality_file " + self.tmp + "/tokenized_quality.txt" + \
                        " --tmp " + self.tmp + \
                        " --thread " + self.thread + \
                        " --label_method DPDN" + \
                        " --max_positives -1" + \
                        " --min_sup " + self.min_sup
        os.system(command)

    def save_models(self):
        print("===Saving Model and Results===")
        shutil.copy2(self.tmp+"/segmentation.model", self.model+"/segmentation.model")
        shutil.copy2(self.tmp+"/token_mapping.txt", self.model+"/token_mapping.txt")

    def generate_output_training(self):
        print("===Generating Output===")
        token_mapping = self.model + "/token_mapping.txt"
        command = "java " + self.tokenizer + " -m translate -i " + self.tmp+"/final_quality_multi-words.txt" + " -o " + self.model+"/AutoPhrase_multi-words.txt" + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)
        command = "java " + self.tokenizer + " -m translate -i " + self.tmp+"/final_quality_unigrams.txt" + " -o " + self.model+"/AutoPhrase_single-words.txt" + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)
        command = "java " + self.tokenizer + " -m translate -i " + self.tmp+"/final_quality_salient.txt" + " -o " + self.model+"/AutoPhrase.txt" + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)


    @staticmethod
    def phrasal_segment(filename, model_path=None, pretrained_model=None, language="EN", pos_tagging=True, highlight_multi=0.5, highlight_single=0.8, thread=10):
        a = Autophrase(filename=filename, model_path=model_path, pretrained_model=pretrained_model, language=language, pos_tagging=pos_tagging, highlight_multi=highlight_multi, highlight_single=highlight_single, thread=thread)
        a.tokenize_text_to_seg()
        a.pos_tagging_text_to_seg()
        a.phrase_segmentation()
        a.generate_output_text_to_seg()

    def tokenize_text_to_seg(self):
        token_mapping = self.model + "/token_mapping.txt"
        print("===Tokenization===")
        tokenized_text_to_seg = self.tmp + "/tokenized_text_to_seg.txt"
        command = "java " + self.tokenizer + " -m direct_test -i " + self.text_to_seg + " -o " + tokenized_text_to_seg + " -t " + token_mapping + " -c N -thread " + self.thread
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)

    def pos_tagging_text_to_seg(self):
        if self.language != "JA" and self.language != "CN" and self.language != "AR" and self.enable_pos_tagging == True:
            print("===Part-Of-Speech Tagging===")  
            raw = self.tmp + "/raw_tokenized_text_to_seg.txt"            
            pos_tag(self.language, int(self.thread), raw, self.tmp)
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

    def generate_output_text_to_seg(self):
        print("===Generating Output===")
        command = "java " + self.tokenizer + " -m segmentation -i " + self.text_to_seg
        command = command + " -segmented " + self.tmp + "/tokenized_segmented_sentences.txt"
        command = command + " -o " + self.model + "/segmentation.txt"
        command = command + " -tokenized_raw " + self.tmp + "/raw_tokenized_text_to_seg.txt"
        command = command + " -tokenized_id " + self.tmp + "/tokenized_text_to_seg.txt -c N"
        if self.language == "AR":
            command = command + " -tagger_model " + self.tagger_model
        os.system(command)

#Autophrase.phrasal_segment("DBLP.5K.txt")
#Autophrase.phrasal_segment("bbc.txt", language='AR')
#Autophrase.train_model(trainfile="DBLP_full.txt", language='EN')
#Autophrase.train_model("bbc.txt", language='AR')