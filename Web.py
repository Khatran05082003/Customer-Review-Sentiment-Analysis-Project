import pandas as pd
import streamlit as st
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
lemma = WordNetLemmatizer()
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
import re
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm

def clean(x):
    x = re.sub('[^a-zA-Z0-9]',' ', str(x))
    x = x.lower()
    x = x.split()
    x = [lemma.lemmatize(word) for word in x if word not in set(stopwords.words("english"))]
    x = " ".join(x)
    return x

st.header('Sentiment Analysis')
with st.expander('Analyze Text'):
    text = st.text_input('Text here: ')
    if text:
        vds = SentimentIntensityAnalyzer()
        sentiment = vds.polarity_scores(text)
        st.write('Neg: ', round(sentiment['neg'],2))
        st.write('Neu: ', round(sentiment['neu'],2))
        st.write('Pos: ', round(sentiment['pos'],2))

    pre = st.text_input('Clean Text: ')
    if pre:
        st.write(clean(pre))

with st.expander('Analyze CSV'):
    upl = st.file_uploader('Upload file')

    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    def polarity_scores_roberta(example):
        encoded_text = tokenizer(example, return_tensors='pt')
        output = model(**encoded_text)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        scores_dict = {
            'roberta_neg' : scores[0],
            'roberta_neu' : scores[1],
            'roberta_pos' : scores[2]
        }
        return scores_dict
    


    def determine_sentiment(scores_dict):
        max_score_label = max(scores_dict, key=scores_dict.get)
        return max_score_label

    if upl:
        df = pd.read_csv(upl)
        del df['Unnamed: 0']
        df['score'] = df['corpus'].apply(polarity_scores_roberta)
        df['analysis'] = df['score'].apply(determine_sentiment)
        st.write(df.head(10))

        @st.cache
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='sentiment.csv',
            mime='text/csv',
        )