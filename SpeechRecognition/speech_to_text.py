import http.client as httplib
try:
    import speech_recognition as sr
except ImportError as e:
    print('ERROR: Cannot find module "speech_recognition." Speech activation command utitlity will be deactivated.')
    print("Try run `pip install pyaudio` and `pip install SpeechRecognition`")


def is_internet_connected() -> bool:
    connection = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        connection.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        connection.close()

def get_speech_command():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        if not is_internet_connected():
            raise ConnectionError("status code 404. Not Found. Please connect to internet for using speech-to-text.")
        commands = recognizer.recognize_google(audio)
        print(commands)
        return commands
    except Exception as e:
        print("ERROR: ", str(e))

get_speech_command()