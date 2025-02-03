import runpod

def reverse_string(string):
    return string[::-1]

def handler(job):
    print(f"string-reverser | Starting job {job['id']}")

    job_input = job["input"]

    string = job_input.get("text", "")

    if not string:
        return {
            "error" : "ValueError : No input text provided"
        }
    
    reversed_string = reverse_string(string)

    job_output = {
        "original_text" : string,
        "reversed_text" : reversed_string
    }

    return job_output 


runpod.serverless.start({
    "handler" : handler
})