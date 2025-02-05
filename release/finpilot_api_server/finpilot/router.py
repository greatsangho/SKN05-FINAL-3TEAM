
async def route_question(state):
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
		print("[Graph Log] ROUTE QUESTION to 'draft'")
		return "draft"
	elif chat_option == "요약 / 확장":
		print("[Graph Log] ROUTE QUESTION to 'length_control'")
		return "length_control"
	elif chat_option == "데이터 시각화 (Web)":
		print("[Graph Log] ROUTE QUESTION to 'visualize_web_data'")
		return "visualize_web_data"
	elif chat_option == "데이터 시각화 (Upload)":
		print("[Graph Log] ROUTE QUESTION to 'visualize_upload_data'")
		return "visualize_upload_data"
	elif chat_option == "단락 생성":
		print("[Graph Log] ROUTE QUESTION to 'paragraph'")
		return "paragraph"