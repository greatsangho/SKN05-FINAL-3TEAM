import runpod
import time
import re
import json
import sys

def text_to_speech_simulator(text, chunk_size=5, delay=0.5):
    words = re.findall(r'\w+', text)

    for i in range(0, len(words), chunk_size):
        chunk = words[i : i+chunk_size]
        audio_chunk = f"Audio chunk {i // chunk_size + 1} : {' '.join(chunk)}"
        time.sleep(delay)
        yield audio_chunk


def generator_handler(job):
    job_input = job["input"]

    text = job_input.get("text", "Welcome to RunPod's text-to-speech simulator!")
    chunk_size = job_input.get('chunk_size', 5)
    delay = job_input.get('delay', 0.5)

    print(f"TTS Simulator | Starting job {job['id']}")
    print(f"Processing text: {text}")

    for audio_chunk in text_to_speech_simulator(text, chunk_size, delay):
        yield {"status": "processing", "chunk": audio_chunk}
    
    yield {"status": "completed", "message": "Text-to-speech conversion completed"}


if __name__ == "__main__":
    if "--test_input" in sys.argv:
        test_input_index = sys.argv.index("--text_input")
        if test_input_index + 1 < len(sys.argv):
            test_input_json = sys.argv[test_input_index + 1]
            try :
                job = json.loads(test_input_json)
                gen = generator_handler(job)
                for item in gen:
                    print(json.dumps(item))
            except json.JSONDecodeError:
                print("Error : Invaild JSON in test_input")
        else:
            print("Error : --test_input requires a JSON string argument")
    else:
        runpod.serverless.start({"handler" : generator_handler})
