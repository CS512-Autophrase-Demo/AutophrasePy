from autophrase import *
a = Autophrase()
a.tokenize("README.md")
a.pos_tagging()
a.phrase_segmentation()
a.generate_output()
