# NLP-draft-system

    analysis.py

    USAGE:
    BY DEFUALT THE MODEL RUNS THE OPTIMAL PARAMETERS FOR THE DEVELOPMENTS SET
    -t runs the model on the test dataset as opposed to the development dataset
    -b [1,2,3,4] Baseline Models
        1: run the SIMPLE model
        2: run the BASIC-CONTEXT model
        3: run the BAG-OF-BIGRAMS model
        4: run the REWARD LONGER EVALUATION model with curve of 0.99995
    -w [INTEGER] word multiply weight (default 150)
    -p [INTEGER] projection multiply weight (default 250)
    -c [FLOAT] Longer Evaluation curve (0-1, default 0.99995)
    -m [INTEGER] minimum count (default 5)
    -r [INTEGER] maximum range (default 75)
