import dialogflow_v2 as dialogflow
import pyaudio
import os
import wave

#sudo apt-get install portaudio19-dev python-pyaudio
#pip install pyaudio


##AUDIO INPUT
#FORMAT = pyaudio.paInt16
#CHANNELS = 1
#RATE = 44100
#CHUNK = 1024
#RECORD_SECONDS = 2
#WAVE_OUTPUT_FILENAME = "output.wav"
#
#audio = pyaudio.PyAudio()
#
## start Recording
#stream = audio.open(format=FORMAT, channels=CHANNELS,
#                rate=RATE, input=True,
#                frames_per_buffer=CHUNK)

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

#fs=44100
#duration = 3  # seconds
#
##myrecording = sd.playrec(myarray, fs, channels=2)
#
#myrecording = sd.rec(duration * fs, samplerate=fs, channels=2, dtype='float64')
#print (f"Recording Audio for {duration} seconds")
#sd.wait()
#print ("Audio recording complete , Playing recorded Audio")
#sd.play(myrecording, fs)
#sd.wait()
#print ("Play Audio Complete")

def get_stream():
    
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 3
    
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    
    print('Recording')
    
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    
    frames = []  # Initialize array to store frames
    
    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
    
    print('Finished recording')





def detect_intent_stream(project_id, session_id, audio_file_path,
                         language_code):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    
    session_client = dialogflow.SessionsClient()

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = 44100

    session_path = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session_path))

    def request_generator(audio_config, audio_file_path):
        query_input = dialogflow.types.QueryInput(audio_config=audio_config)

        # The first request contains the configuration.
        yield dialogflow.types.StreamingDetectIntentRequest(
            session=session_path, query_input=query_input)

        # Here we are reading small chunks of audio data from a local
        # audio file.  In practice these chunks should come from
        # an audio input device.
        with open(audio_file_path, 'rb') as audio_file:
            while True:
                chunk = audio_file.read(4096)
                if not chunk:
                    break
                # The later requests contains audio data.
                yield dialogflow.types.StreamingDetectIntentRequest(
                    input_audio=chunk)

    audio_config = dialogflow.types.InputAudioConfig(
        audio_encoding=audio_encoding, language_code=language_code,
        sample_rate_hertz=sample_rate_hertz)

    requests = request_generator(audio_config, audio_file_path)
    responses = session_client.streaming_detect_intent(requests)

    print('=' * 20)
    for response in responses:
        print('Intermediate transcript: "{}".'.format(
                response.recognition_result.transcript))

    # Note: The result from the last response is the final transcript along
    # with the detected content.
    query_result = response.query_result

    print('=' * 20)
    print('Query text: {}'.format(query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        query_result.intent.display_name,
        query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
        query_result.fulfillment_text))
5
def main():
#    DIALOGFLOW_PROJECT_ID = 'newagent-njlomn'
    DIALOGFLOW_LANGUAGE_CODE = 'ru'
    GOOGLE_APPLICATION_CREDENTIALS = 'personal-robot-f1fe0b4362b4.json'
    SESSION_ID = 'current-user-id'
    
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
    
    import google.auth
    credentials, project = google.auth.default()
    
#    audio = get_stream()
    
    fs=44100
    duration = 3  # seconds
    
    #myrecording = sd.playrec(myarray, fs, channels=2)
    print('recording')
    myrecording = sd.rec(duration * fs, samplerate=fs, channels=2, dtype='float64')
    from scipy.io.wavfile import write
    write('output.wav', fs, myrecording)
    print('recorded')
    print('identifying intent')
    detect_intent_stream(project, SESSION_ID, 'output.wav', DIALOGFLOW_LANGUAGE_CODE)
    
if __name__ == '__main__':
    main()