from pymongo import MongoClient
from pymongo.database import Database
import os
import json

# global client
client: MongoClient = None
db: Database = None


def db_connect():
    """
    Connects to the MongoDB instance and returns a client object.
    The `MONGO_URI` environment variable should be set to the URI of the MongoDB instance.
    This function will load the environment variables from the `config.json` file
    if they have not been set already.
    Returns:
        A pymongo.mongo_client.MongoClient object.
    """

    global client
    if client is None:
        load_env()
        mongo_uri = os.environ['MONGO_URI']
        client = MongoClient(mongo_uri)
    return client


def get_database():
    """
    Retrieves the 'ragchatdb' database from the connected MongoDB client.

    This function establishes a connection to the MongoDB instance using `db_connect()`
    and then accesses the 'ragchatdb' database.

    Returns:
        Database: The 'ragchatdb' database object.
    """
    global db
    if db is None:
        db = db_connect().get_database("ragchatdb")
    return db


def load_env():
    """
    Loads the environment variables from the `config.json` file.

    This function checks if the environment variables are not already set.
    If they are not set, it will load the configuration from the `config.json` file
    and set the environment variables accordingly.

    The following environment variables are set:
    - `GEMINI_API_KEY`: The API key of the Gemini model.
    - `MODEL`: The model name of the Gemini model.
    - `MONGO_URI`: The connection string of the MongoDB instance.

    Returns:
        None
    """
    print("Start:load_env")
    config_file_path = os.path.join(os.path.dirname(__file__),'resources\\config.json')

    with open(config_file_path, "r") as f:
        config = json.load(f)
        os.environ['LLAMA_API_KEY'] = config["groq_llama"]['LLAMA_API_KEY']
        os.environ['LLAMA_MODEL_NAME'] = config["groq_llama"]['LLAMA_MODEL_NAME']
        os.environ["LLAMA_API_URL"] = config["groq_llama"]['LLAMA_API_URL']
        os.environ["LLAMA_MAX_TOKENS"] = config["groq_llama"]['LLAMA_MAX_TOKENS']
        os.environ["LLAMA_TEMPERATURE"] = config["groq_llama"]['LLAMA_TEMPERATURE']
        os.environ["LLAMA_TOP_P"] = config["groq_llama"]['LLAMA_TOP_P']
        os.environ["LLAMA_FREQUENCY_PENALTY"] = config["groq_llama"]['LLAMA_FREQUENCY_PENALTY']
        os.environ["LLAMA_PRESENCE_PENALTY"] = config["groq_llama"]['LLAMA_PRESENCE_PENALTY']

        os.environ['OPENAI_API_KEY'] = config["openai"]['OPENAI_API_KEY']
        os.environ['OPENAI_MODEL'] = config["openai"]['OPENAI_MODEL']
        os.environ["OPENAI_API_URL"] = config["openai"]['OPENAI_API_URL']
        os.environ["OPENAI_MAX_TOKENS"] = config["openai"]['OPENAI_MAX_TOKENS']
        os.environ["OPENAI_TEMPERATURE"] = config["openai"]['OPENAI_TEMPERATURE']
        os.environ["OPENAI_TOP_P"] = config["openai"]['OPENAI_TOP_P']
        os.environ["OPENAI_FREQUENCY_PENALTY"] = config["openai"]['OPENAI_FREQUENCY_PENALTY']
        os.environ["OPENAI_PRESENCE_PENALTY"] = config["openai"]['OPENAI_PRESENCE_PENALTY']


        os.environ['GEMINI_API_KEY'] = config["google"]['GEMINI_API_KEY']
        os.environ['GEMINI_MODEL'] = config["google"]['GEMINI_MODEL']
        config_file_path = os.path.join(os.path.dirname(__file__), config['google']['GOOGLE_APPLICATION_CREDENTIALS'])
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config_file_path
        os.environ['MONGO_URI'] = config['database']['uri']
