############################# Import Modules #############################
# text magician
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# messages
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages

import os



class LengthControlProcess:
    def __init__(self):
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.5,
        )

        self.length_controller = llm | StrOutputParser()
    
    async def length_control_node(self, state):
        """
        Summary / Expand the given text.

        Args : 
            state (dict) : The current graph state

        Returns :
            state (dict) : New key added to state, generation, that contains LLM generation
        """

        print("[Graph Log] LENGTH CONTROL ...")

        question = state["question"]
        updated_messages = add_messages(state["messages"], HumanMessage(content=question))
        state["messages"] = updated_messages

        generation = await self.length_controller.ainvoke([HumanMessage(content=question)])

        state["generation"] = generation
        updated_messages = add_messages(state["messages"], AIMessage(content=generation))
        state["messages"] = updated_messages

        return state
