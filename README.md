# sunuselfie

## Start

```bash
# create conda environment from environment.yml
conda env create -f environment.yml
# activate conda environment
conda activate sunuselfie
# run the app
streamlit run main.py
```

if error occurs it's probably the dlib package, try to install it manually with `conda install -c conda-forge dlib`
