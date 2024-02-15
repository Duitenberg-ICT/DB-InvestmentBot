import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
import spacy
import string
from typing import List


nlp = spacy.load("en_core_web_sm")


def download_nltk_resources():
    """
    The method downloads the necessary resources for the nltk library.
    """
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    nltk.download("maxent_ne_chunker")
    nltk.download("words")
    nltk.download("wordnet")
    nltk.download("stopwords")


def preprocess(text) -> str:
    """
    The method performs basic preprocessing of the text before training the model. This includes:
    - converting the text to lowercase
    - removing non-ASCII characters
    - removing brand names
    - removing punctuation
    - lemmatization

    Parameters
    ----------
    text : str
        The text for preprocessing.

    Returns
    -------
    str
        The preprocessed text.
    """
    text_ascii = text.encode("ascii", errors="ignore").decode()
    text_no_brands = _remove_brands(text_ascii)
    text_lower = text_no_brands.lower()
    text_nonwords = re.sub("[^A-Za-z0-9 ]\w+[^A-Za-z0-9]*", " ", text_lower)
    text_no_punctuation = text_nonwords.translate(
        str.maketrans("", "", string.punctuation)
    )
    text_lemmatization = _lemmatize(text_no_punctuation)
    return text_lemmatization


def fetch_companies(text, custom_nlp=None) -> List[str]:
    """
    The method finds all names of organizations in the text.

    Parameters
    ----------
    text : str
        The text for analysis.

    Returns
    -------
    List[str]
        A list of strings that represent names of companies.

    Raises
    ------
    ValueError
        If no companies are found in the text.
    """

    if custom_nlp is None:
        custom_nlp = nlp

    companies = []
    doc = custom_nlp(text)
    for entity in doc.ents:
        if entity.label_ == "ORG":
            companies.append(entity.text)

    if len(companies) == 0:
        raise ValueError("No companies found in the text.")

    return companies


def _remove_brands(text, custom_nlp=None) -> str:
    """
    Only for internal use.
    The method removes the names of companies from the text.

    Parameters
    ----------
    text : str
        The text for analysis.

    Returns
    -------
    str
        The text without the names of companies.
    """

    if custom_nlp is None:
        custom_nlp = nlp

    doc = custom_nlp(text)
    filtered_text = []
    for token in doc:
        # Check if the token is a named entity and not recognized as an organization
        if token.ent_type_ != "ORG":
            filtered_text.append(token.text)
    return " ".join(filtered_text)


def _lemmatize(text) -> str:
    """
    Only for internal use.
    The method lemmatizes the text.

    Parameters
    ----------
    text : str
        The text for lemmatization.

    Returns
    -------
    str
        The lemmatized text.
    """

    sw = stopwords.words("english")
    wnl = WordNetLemmatizer()
    return " ".join([wnl.lemmatize(w, "v") for w in text.split() if w not in sw])
