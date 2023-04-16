import http.client as httplib
import warnings
import logging
logger = logging.getLogger(__name__)
from core.utils import silence_function

try:
    import speech_recognition as sr
except ImportError as e:
    logger.critical("Cannot find module 'speech_recognition.' Try run `pip install pyaudio` and `pip install SpeechRecognition`")


def is_internet_connected(ip_adresses: tuple=("8.8.8.8", "8.8.4.4")) -> bool:
    """
    :param ip_adresses: Goggle's public DNS servers. Helps avoiding DNS resolution, 
    application layer connections and calls to external utilities from Python.
    """
    for ip in ip_adresses:
        connection = httplib.HTTPSConnection(ip, timeout=5)
        try:
            connection.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            connection.close()


class NLPCommandHandler:
    """
    Handles Natural Language Processing and determines whether user is calling for AI to overtake the thinking
    """

    activation_keywords = {"difficult", "position", "think", "let", "clueless", "i", "don't know", "i am", "i'm", "what", "do", "desperate", "uncertain", "god", "help"}
    
    @classmethod
    def init(cls, keywords: list | tuple=None, activation_threshold=2):
        """
        :param activation_threshold: the number of keywords that has to be met in oder for the search to start
        """
        try:
            cls.recognizer = sr.Recognizer()
        except Exception as e:
            logger.error(e, "You might have to install missing modules. Make sure all requirements are met")
        else:
            cls.recognizer.pause_threshold = 0.5
        cls.activation_keywords = keywords or cls.activation_keywords
        cls.activation_threshold = activation_threshold

    @classmethod
    def speech_to_text(cls) -> str:
        text = ""
        try:
            # Using standard mic input
            with sr.Microphone() as source:
                print("Listening...")
                audio = cls.recognizer.listen(source)
            if not is_internet_connected():
                warnings.warn("status code 404. Not Found. Please connect to internet for using speech-to-text.")
            with silence_function(): # This is to suppress the internal console outputs of recognize_google
                # Where the magic happens
                text = cls.recognizer.recognize_google(audio)
        except Exception as e:
            logger.error(e)
        return text

    @classmethod
    def listen_for_activation(cls) -> bool:
        commands = cls.speech_to_text()
        commands = commands.lower()
        logger.info(commands)
        keyword_counter = len(list(filter(lambda kw: kw in commands, cls.activation_keywords)))
        return keyword_counter >= cls.activation_threshold