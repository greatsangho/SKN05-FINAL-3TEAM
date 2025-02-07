######################################## Import Modules ########################################
# from pydantic import BaseModel, Field
# from typing import Literal
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_core.prompts import ChatPromptTemplate


def route_question(state):
	"""
	Route question to certain process
	
	Args : 
		state (dict) : The current graph state
		
	Returns : 
		str : Next node to call
	"""
	
	print("[Graph Log] ROUTE QUESTION ...")
	
	chat_option = state["chat_option"]
	if chat_option == "초안 생성":
		print("[Graph Log] ROUTE QUESTION to 'draft_writer'")
		return "draft"
	elif chat_option == "요약 / 확장":
		print("[Graph Log] ROUTE QUESTION to 'text_magician'")
		return "text_magician"
	elif chat_option == "데이터 시각화 (Web)":
		print("[Graph Log] ROUTE QUESTION to 'web_visualizer'")
		return "web_visualizer"
	elif chat_option == "데이터 시각화 (Upload)":
		print("[Graph Log] ROUTE QUESTION to 'inner_visualizer'")
		return "inner_visualizer"
	elif chat_option == "단락 생성":
		print("[Graph Log] ROUTE QUESTION to 'writer'")
		return "writer"

# def route_question(state):
# 	"""
# 	Route question to certain process
	
# 	Args : 
# 		state (dict) : The current graph state
		
# 	Returns : 
# 		str : Next node to call
# 	"""
	
# 	print("[Graph Log] ROUTE QUESTION ...")
	
# 	question = state["question"]
	
	
# 	if ('요약' in question) or ('확장' in question):
# 		print("[Graph Log] ROUTE QUESTION to 'text_magician'")
# 		return "text_magician"
# 	elif ('조사' in question) and ('시각화' in question):
# 		print("[Graph Log] ROUTE QUESTION to 'web_visualizer'")
# 		return "web_visualizer"
# 	elif (('주어진' in question) and ('시각화' in question)) or (('업로드' in question) and ('시각화' in question)):
# 		print("[Graph Log] ROUTE QUESTION to 'inner_visualizer'")
# 		return "inner_visualizer"
# 	elif ('생성' in question) or ('작성' in question):
# 		print("[Graph Log] ROUTE QUESTION to 'writer'")
# 		return "writer"





########################################### Router Agent ########################################### 
# class RouteQuery(BaseModel):
#     """
#     Route a user query to the most relevant process
#     """

#     process : Literal["writer", "text_magician", "web_visualizer", "inner_visualizer"] = Field(
#         ...,
#         description = "Given a user question choose to route it to 'writer', 'text_magician', 'web_visualizer', 'inner_visualizer'"
#     )

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# llm_router = llm.with_structured_output(RouteQuery)

# system_msg = """
# You are an expert in analyzing user questions and routing them to the most appropriate process.

# Your mission is to interpret the user's question, understand its intent, and route it to one of the following processes:

# 'writer': A process for generating paragraphs or text based on the user's request.
# 'text_magician': A process for summarizing or expanding the text provided by the user within their question.
# 'web_visualizer': A process for creating visualizations requested by the user, based on research or information obtained via web search.
# 'inner_visualizer': A process for creating visualizations based on data uploaded or provided by the user (e.g., CSV files).



# Routing Guidelines
# Analyze the user's question and route it to the appropriate process based on these criteria:

# Route to 'text_magician' if:
# The user's question contains the terms "summarize" or "expand."
# Example: "Please expand this text" or "Summarize the following text for me."

# Route to 'web_visualizer' if:
# The user requests visualization and asks you to research or gather data on a specific topic to generate the visualization.
# Example: "Visualize the GDP trends of the USA for the last 5 years based on web research."

# Route to 'inner_visualizer' if:
# The user has uploaded a CSV file or provided specific data and requests visualization based on it.
# Example: "Generate a visualization using the data I uploaded."

# Route to 'writer' if:
# The user's question does not contain the terms "summarize," "expand," or "draft," and they are requesting new text to be generated.
# Example: "Write a paragraph about the importance of renewable energy."




# Your Task:
# Analyze the user's question thoroughly to understand their intent.
# Determine the appropriate process based on the criteria provided above.
# Route the question to the most relevant process.

# """

# route_prompt = ChatPromptTemplate.from_messages(
#     [
#         SystemMessage(content=system_msg),
#         HumanMessage(content="{question}")
#     ]
# )

# question_router = route_prompt | llm_router

# def route_question(state):
# 	"""
# 	Route question to web search or RAG
	
# 	Args : 
# 		state (dict) : The current graph state
		
# 	Returns : 
# 		str : Next node to call
# 	"""
	
# 	print("[Graph Log] ROUTE QUESTION ...")
	
# 	question = state["question"]
# 	process = question_router.invoke({"question" : question})
	
# 	if process.process == "writer":
# 		print("[Graph Log] ROUTE QUESTION to 'writer'")
# 		return "writer"
# 	elif process.process == "text_magician":
# 		print("[Graph Log] ROUTE QUESTION to 'text_magician'")
# 		return "text_magician"
# 	elif process.process == "web_visualizer":
# 		print("[Graph Log] ROUTE QUESTION to 'web_visualizer'")
# 		return "web_visualizer"
# 	elif process.process == "inner_visualizer":
# 		print("[Graph Log] ROUTE QUESTION to 'inner_visualizer'")
# 		return "inner_visualizer"