import os
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, POLYGON_API_KEY, USER_AGENT

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY
os.environ['USER_AGENT'] = USER_AGENT
os.environ['POLYGON_API_KEY'] = POLYGON_API_KEY




from finpilot.core import FinPilot
import runpod


def finpilot_handler(job):
    job_input = job["input"]
    user_question = job_input["question"]

    app = FinPilot()

    result = app.invoke(question=user_question)

    