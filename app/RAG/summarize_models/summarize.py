from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import BartForConditionalGeneration, BartTokenizer


class Summarize:
    bart_model: BartForConditionalGeneration;
    bart_tokenizer: BartTokenizer;
    pegasus_model: PegasusForConditionalGeneration;
    pegasus_tokenizer: PegasusTokenizer;

    def __init__(self):
        # 1. Load the pre-trained model and tokenizer
        bart_model_name = "facebook/bart-large-cnn"
        self.bart_model = BartForConditionalGeneration.from_pretrained(bart_model_name)
        self.bart_tokenizer = BartTokenizer.from_pretrained(bart_model_name)
        # 1. Load the pre-trained model and tokenizer
        pegasus_model_name = "google/pegasus-xsum"
        self.pegasus_model = PegasusForConditionalGeneration.from_pretrained(pegasus_model_name)
        self.pegasus_tokenizer = PegasusTokenizer.from_pretrained(pegasus_model_name)

    def summarize_text_with_bart(self, text):
        """
        Summarizes the given text using the Facebook BART-Large-CNN model.
        Args:
          text: The input text to be summarized.
        Returns:
          The generated summary.
        """

        # 1. Load the pre-trained model and tokenizer
        # check if it has been initialized
        # 2. Tokenize the input text
        #    - This converts the text into numerical representations
        #    - that the model can understand.
        inputs = self.bart_tokenizer(text, max_length=1024, return_tensors="pt", truncation=True)
        # 3. Generate the summary using the model
        #    - `num_beams`: Controls the number of sequences explored during beam search
        #                  (higher values may improve quality but increase inference time).
        #    - `max_length`: Sets the maximum length of the generated summary.
        summary_ids = self.bart_model.generate(inputs["input_ids"], num_beams=4, max_length=100)

        # 4. Decode the generated summary
        #    - Convert the numerical representation back into human-readable text.
        summary = self.bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary

    def summarize_text_with_pegasus(self, text):
        """
        Summarizes the given text using the Pegasus model.
        Args:
          text: The input text to be summarized.
        Returns:
          The generated summary.
        """
        # 2. Tokenize the input text
        inputs = self.pegasus_tokenizer(text, return_tensors="pt", truncation=False)

        # 3. Generate the summary using the model
        summary_ids = self.pegasus_model.generate(inputs["input_ids"], num_beams=4, max_length=100)

        # 4. Decode the generated summary
        summary = self.pegasus_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary

    def summarize_text(self, text, model):
        if model == "pegasus":
            return self.summarize_text_with_pegasus(text)
        elif model == "bart":
            return self.summarize_text_with_bart(text)
        else:
            raise ValueError(f"Unsupported model: {model}")


if __name__ == "__main__":
    # Example usage
    # input_text = "This is an example of some input text. It can be long and complex, but the model will try to summarize it concisely."
    summarize_text_with_bart = Summarize().summarize_text_with_bart
    input_text = "Nvidia stock (NVDA) fell nearly 2% Monday after the Biden administration released an updated export rule aimed at controlling the flow of artificial intelligence chips to 'adversaries' such as China."
    summary_1 = summarize_text_with_bart(input_text)
    print(f"Summarize_text_with_bart: {summary_1}")
    # Example usage

    summarize_text_with_pegasus = Summarize().summarize_text_with_pegasus
    # input_text = "This is an example of some input text. It can be long and complex, but the model will try to summarize_models it concisely."
    input_text = "Nvidia stock (NVDA) fell nearly 2% Monday after the Biden administration released an updated export rule aimed at controlling the flow of artificial intelligence chips to 'adversaries' such as China."

    summary_2 = summarize_text_with_pegasus(input_text)
    print(f"Summarize_text_with_pegasus: {summary_2}")
