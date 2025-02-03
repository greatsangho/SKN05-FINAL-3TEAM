from finpilot.core import FinPilot
import runpod

def finpilot_handler(job):
    job_input = job["input"]
    user_question = job_input["question"]

    app = FinPilot()

    result = app.invoke(question=user_question)

    job_output = {
        "question" : user_question,
        "finpilot_answer" : result
    }

    return job_output 


runpod.serverless.start({"handler" : finpilot_handler})