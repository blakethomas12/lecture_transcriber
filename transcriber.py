import speech_recognition as sr
import google.generativeai as genai
import threading

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

# Define the file paths
transcription_file_path = 'live_transcription.txt'
summary_file_path = "summaries/"+input("Enter the name of the summary file(no .txt): ")+".txt"

open(transcription_file_path, 'w').close()

unknown_errors = 0

key = "YOUR_API_KEY_HERE"

# Configure Google Gemini API
genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-1.5-flash")

prompt = "summarize this, list me major topics, any keywords, anything important to know or that I need to keep in mind, this is only a part of the total lecture, also keep in mind that this transcript has been automaticaly generated and there might be some errors:"

stop_flag = threading.Event()

def transcribe_audio(text):
    try:
      with open(transcription_file_path, 'a') as trans_file:
            trans_file.write(text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def record_audio():
    global unknown_errors
    print("Recording...")
    while not stop_flag.is_set():
        try:
            with sr.Microphone() as source:

                r.adjust_for_ambient_noise(source, duration=.2)

                audio = r.listen(source)

                text = r.recognize_google(audio)
                transcribe_audio(text)
            
        except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
        except sr.UnknownValueError as e:
                # print("unknown error occured")
                unknown_errors += 1

def stop_recording():
    while True:
        user_input = input("Enter 'stop' to finish recording: ")
        if user_input == 'stop':
            stop_flag.set()
            print("Finishing...")
            break

recording_thread = threading.Thread(target=record_audio)
recording_thread.start()
stop_recording()

recording_thread.join()

print("Recording complete.")
print("Unknown Words or Phrases: ", unknown_errors)



print("Summarizing...")
with open(summary_file_path, 'w') as sum_file:
    try:
        with open(transcription_file_path, 'r') as tf:
            transcription_text = tf.read()

            CHUNK_SIZE = 2000
            for i in range(0, len(transcription_text), CHUNK_SIZE):
                chunk = transcription_text[i:i+CHUNK_SIZE]
                response = model.generate_content(prompt + chunk)
                sum_file.write(response.text + '\n')

            print("Summarization complete.")

    except Exception as e:
        print(f"Error during summarization: {e}")


print("Done.")
