# sunuselfie

## Start

create a .env file with the following content:

```bash
CONSUMER_KEY=your_twitter_consumer_key
CONSUMER_SECRET=your_twitter_consumer_secret
ACCESS_TOKEN=your_twitter_access_token
ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

then run the following commands:

```bash
# create conda environment from environment.yml
conda env create -f environment.yml
# activate conda environment
conda activate sunuselfie
# run the app
streamlit run main.py
```

if error occurs it's probably the dlib package, try to install it manually with `conda install -c conda-forge dlib`
