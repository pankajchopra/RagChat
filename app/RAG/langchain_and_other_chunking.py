from langchain import requests
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter, HTMLHeaderTextSplitter
import re
from bs4 import BeautifulSoup
import nltk

nltk.data.path.append('../../models/nltk_data')


class Chunking:
    def __init__(self):
        pass

    @staticmethod
    def chunk_recursive_character_text_splitter_text(text: [str], chunk_size=1000, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        texts = text_splitter.create_documents(text)
        return texts

    @staticmethod
    def chunk_character_text_splitter_text(self, text, chunk_size=1000, chunk_overlap=200):
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        texts = text_splitter.create_documents([text])
        return texts

    @staticmethod
    def chunk_html_selector_text(self, text=None, web_url=None, headers_to_split_on=[], chunk_size=1000, chunk_overlap=200):
        response = requests.get(web_url)
        if response.status_code == 200:
            html_doc = response.text
        else:
            raise Exception(f"Error: {response.status_code}")
        if headers_to_split_on == []:
            raise ValueError("Headers to split on cannot be empty.")
        # //example
        # headers_to_split_on = [
        #     ("h1", "Header 1"),
        #     ("p", "paragraph")
        # ]

        html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        html_header_splits = html_splitter.split_text(html_doc)

        return html_header_splits

    def extract_plan_text_from_website(url):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}")
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ' '.join([p.text for p in soup.find_all('p')])
            """Removes non-printable characters from a string."""
            printable_chars = set(text.printable)
            text = ''.join(c for c in text if c in printable_chars)
            # Remove special characters and numbers
            text = re.sub(r"[^a-zA-Z]", " ", text)
            return text

    # Chunking Function
    def chunk_sentence_based_text(text, max_length=128):
        """
        Splits a given text into chunks, where each chunk is a sentence.

        Args:
            text (str): The text to be split.
            max_length (int): The maximum number of characters in a chunk.
                Defaults to 128.

        Returns:
            list[str]: A list of strings, where each string is a sentence
                from the input text.
        """
        sentences = nltk.sent_tokenize(text)
        return sentences

    # Hybrid  Chunking Function
    def hybrid_chunking(text, max_tokens_per_chunk, chunk_overlap=100):
        """
        This function takes a text (a list of strings) and splits it into chunks by tokenizing the text
        and grouping the tokens into chunks of a given maximum size.
        If the tokens in a sentence exceed the maximum size, the sentence is split into multiple chunks.

        Args:
            text (list[str]): A list of strings representing the text to be split.
            max_tokens_per_chunk (int): The maximum number of tokens per chunk.

        Returns:
            list[str]: A list of strings, where each string is a chunk of text.
        """
        sentences = nltk.sent_tokenize(' '.join(text))
        chunks = []
        current_chunk = []
        current_tokens = 0
        overlap = chunk_overlap
        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            if current_tokens + len(tokens) <= max_tokens_per_chunk:
                current_chunk.append(sentence)
                current_tokens += len(tokens)
            else:
                chunks.append(" ".join(current_chunk))
                # Keep the last `chunk_overlap` tokens for the next chunk
                overlap_tokens = current_chunk[-1].split()[-chunk_overlap:] if len(current_chunk) > 0 else []

                # Start a new chunk with the overlap tokens and the current sentence
                current_chunk = [" ".join(overlap_tokens)] + [sentence]
                current_tokens = len(overlap_tokens) + len(tokens)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
