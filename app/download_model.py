import tensorflow_hub as hub
import tensorflow as tf
import tempfile
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from prometheus_client import REGISTRY

from transformers import AutoTokenizer, AutoModel

import os
import nltk


def download_use_model():
    # Download the Universal Sentence Encoder model to a local folder
    model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    project_root = os.path.dirname(os.path.abspath(__file__))
    # Create a temporary directory
    temp_model_dir = tempfile.mkdtemp()
    print(project_root)
    print("Downloading the Universal Sentence Encoder model...")
    try:
        # Load the model
        embed = hub.load(model_url)
        # Save the model to the specified directory
        tf.saved_model.save(embed, temp_model_dir)
        print(f"Model saved to: {temp_model_dir}")
    except Exception as e:
        print(f"Error loading or saving model: {e}")
    local_model_dir = "./models/universal-sentence-encoder"  # Replace with the desired path


def download_pegasus_model():
    # Specify the directory to save the model
    local_model_dir = "../models/pegasus"

    # Load the Pegasus model and tokenizer from Hugging Face
    model_name = "google/pegasus-xsum"  # You can change this to another model if needed

    # Load model and tokenizer
    model = PegasusForConditionalGeneration.from_pretrained(model_name)
    tokenizer = PegasusTokenizer.from_pretrained(model_name)

    # Create the model directory if it doesn't exist
    os.makedirs(local_model_dir, exist_ok=True)

    # Save the model and tokenizer to the local directory
    model.save_pretrained(local_model_dir)
    tokenizer.save_pretrained(local_model_dir)

    print(f"Pegasus model and tokenizer saved to {local_model_dir}")


def download_nltk_data():
    # Specify the local directory to save the punkt model
    local_dir = "../models/nltk_data"

    # Set the NLTK data path to your local directory
    nltk.data.path.append(local_dir)

    # Download the punkt tokenizer model
    nltk.download('punkt', download_dir=local_dir)

    print(f"punkt model downloaded and saved to {local_dir}")


# def download_all_bert_base():
#
#     # Unregister previously registered metrics
#     collectors = list(REGISTRY._collector_to_names.keys())
#     for collector in collectors:
#         try:
#             REGISTRY.unregister(collector)
#         except KeyError:
#             # Ignore if the collector was already unregistered
#             pass
#
#     modelPath = "../models/bert-base-nli-stsb-mean-tokens"
#
#     tokenizer = AutoTokenizer.from_pretrained("sentence-transformersbert-base-nli-stsb-mean-tokens", cache_dir=modelPath)
#     model = AutoModel.from_pretrained("sentence-transformers/bert-base-nli-stsb-mean-tokens", cache_dir=modelPath)
#
#     print(f"bert-base-nli-stsb-mean-tokens model saved to {modelPath}")


def download_all_mpnet_base_v2():
    # all-MiniLM-L6-v2
    # Specify the local directory where you want to save the model
    # Unregister previously registered metrics
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        try:
            REGISTRY.unregister(collector)
        except KeyError:
            # Ignore if the collector was already unregistered
            pass
    modelPath = "../models/all_mpnet_base_v2"
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2", cache_dir=modelPath)
    model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2", cache_dir=modelPath)

    print(f"Model and tokenizer saved in: {os.path.abspath(modelPath)}")


if __name__ == "__main__":
    # download_use_model();
    # download_pegasus_model();
    # download_nltk_data();
    # download_all_bert_base();
    download_all_mpnet_base_v2();
