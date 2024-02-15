from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax


MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


def polarity_scores(text) -> dict:
    """
    The method calculates the polarity scores for the given text.

    Parameters
    ----------
    example : str
        The text for analysis.

    Returns
    -------
    Dict[str, float]
        A dictionary with the polarity scores.
    """

    encoded_text = tokenizer(text, return_tensors="pt")
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {"negative": scores[0], "neutral": scores[1], "positive": scores[2]}
    return scores_dict
