import re


def clean_text(text):
    text = text.strip()
    text = text.replace('Ɵ', 't')
    text = text.replace('\t', '')
    text = re.sub(r"\s{5,}", " \n", text)
    return re.sub(r"[^\x20-\x7E]", "", text)