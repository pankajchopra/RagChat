import re


def clean_text(text):
    text = text.strip()
    text = text.replace('Ɵ', 't')
    text = text.replace('\t', '')
    text = re.sub(r"\s{5,}", " \n", text)
    return re.sub(r"[^\x20-\x7E]", "", text)


def clean_text_v2(text):
    text = text.strip()
    text = text.replace('Ɵ', 't')
    text = text.replace('\t', '')
    text = text.replace('\n \n', ' ')
    return re.sub(r"\s{5,}", " \n\n", text)


def document_to_dict(document):
    document["_id"] = str(document["_id"])  # Convert ObjectId to string
    return document
