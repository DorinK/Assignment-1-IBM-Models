
README for IBMModel1.py and IBMModel2.py:


In the current working directory should be:
1. IBMModel1.py
2. IBMModel2.py

--------------------------------------------


Two parameters for IBMModel1.py are:
1. A path to the French File
2. A path to the English File
3. y if you want to run model2 (after training model1) and initialize it with the translation parameters of model1; Otherwise, n

Run is as:
  python3 IBMModel1 french_file_path english_file_path your_choise

For example:
  python3 IBMModel1.py word-alignment/data/hansards.f word-alignment/data/hansards.e y
  python3 IBMModel1.py word-alignment/data/hansards.f word-alignment/data/hansards.e n

* An alignments file/s will be outputted to the current working directory.
  A file called 'Model1_alignmentsFile'
  A file called 'Model2_alignmentsFile'(if the third parameter was y)

---------------------------------------------------------------------------------------

Two parameters for IBMModel2.py are:
1. A path to the French File
2. A path to the English File

Run is as:
  python3 IBMModel2 french_file_path english_file_path

For example: 
  python3 IBMModel2.py word-alignment/data/hansards.f word-alignment/data/hansards.e

* An alignments file will be outputted to the current working directory.
  A file called 'Model2_alignmentsFile'

---------------------------------------------------------------------------------------

Notes:

*** You should have nltk library installed in order to run IBMModel1.py and IBMModel2.py

**** I added the eval.py since the original had some minor errors and had an issue with reading the input files' because of encoding type.
