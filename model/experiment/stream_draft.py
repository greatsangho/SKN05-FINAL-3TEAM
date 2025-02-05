import os
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, DART_API_KEY, USER_AGENT, LANGSMITH_API_KEY, LANGSMITH_ENDPOINT, LANGSMITH_PROJECT, LANGSMITH_TRACING
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["DART_API_KEY"] = DART_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_TRACING


from typing_extensions import TypedDict
from typing import Annotated, List
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from finpilot.experimental.draft import DraftProcess
from langgraph.graph import StateGraph, START, END

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import HTTPException



class State(TypedDict):
    question : str
    generation : str
    documents : List[Document]
    messages : Annotated[List[BaseMessage], add_messages]
    source : List[str]
    outlines : List[str]



draft_process = DraftProcess(session_id="session_tmp")

workflow = StateGraph(State)

workflow.add_node("make_outline_node", draft_process.make_outline_node)
workflow.add_node("write_draft_paragraph_node", draft_process.write_draft_paragraph_node)

workflow.add_edge(START, "make_outline_node")
workflow.add_edge("make_outline_node", "write_draft_paragraph_node")
workflow.add_conditional_edges(
    "write_draft_paragraph_node",
    draft_process.should_continue,
    {
        "end" : END,
        "continue" : "write_draft_paragraph_node"
    }
)

app = workflow.compile()





server = FastAPI()
final_state = {}

@server.get("/query")
async def query():
    async def event_stream():
        global final_state
        try:
            async for stream_mode, chunk in app.astream(
                input={
                    "question" : "삼성전자 기업분석 보고서 초안 작성해줘"
                },
                stream_mode=["custom"]
            ):
                if isinstance(chunk, dict):
                    final_state = chunk
                else:
                    yield f"{chunk}"
        except Exception as e:
            raise HTTPException(500, f"Internel Server Error : \n{e}")
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@server.get("/get_source")
async def get_source():
    global final_state
    source = final_state["source"]
    final_state = {}
    return JSONResponse(content={"source" : source})

if __name__ == "__main__":
    uvicorn.run("stream_draft:server", host='localhost', reload=True)





















# {'agent': 
#  {'messages': 
#   [
#       AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_ybDmOrmEE4pZ6NQifOr7We5S', 'function': {'arguments': '{"corp_name": "삼성전자", "start_date": "2024-01-01", "end_date": "2024-12-31"}', 'name': 'fetch_stock_data'}, 'type': 'function'}, {'id': 'call_fzob2lqGhp5T8tROS20sNA75', 'function': {'arguments': '{"corp_name": "삼성전자", "report_year": "2024"}', 'name': 'fetch_financial_data'}, 'type': 'function'}, {'id': 'call_vaXBlOlBxXaCoO5tAa2v0mb7', 'function': {'arguments': '{"query": "삼성전자"}', 'name': 'fetch_company_news'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 97, 'prompt_tokens': 852, 'total_tokens': 949, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-2024-08-06', 'system_fingerprint': 'fp_4691090a87', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-0de8f59d-b41f-4544-a4f0-a45a7f896b0e-0', tool_calls=[{'name': 'fetch_stock_data', 'args': {'corp_name': '삼성전자', 'start_date': '2024-01-01', 'end_date': '2024-12-31'}, 'id': 'call_ybDmOrmEE4pZ6NQifOr7We5S', 'type': 'tool_call'}, {'name': 'fetch_financial_data', 'args': {'corp_name': '삼성전자', 'report_year': '2024'}, 'id': 'call_fzob2lqGhp5T8tROS20sNA75', 'type': 'tool_call'}, {'name': 'fetch_company_news', 'args': {'query': '삼성전자'}, 'id': 'call_vaXBlOlBxXaCoO5tAa2v0mb7', 'type': 'tool_call'}], usage_metadata={'input_tokens': 852, 'output_tokens': 97, 'total_tokens': 949, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})
#   ]
#  }
# }
# {'tools': 
#  {'messages': 
#   [
#       ToolMessage(content='Error: AttributeError("module \'asyncio\' has no attribute \'to_trhead\'")\n Please fix your mistakes.', name='fetch_stock_data', id='d5c7cb24-b7fc-44fd-91ea-466cb5b61484', tool_call_id='call_ybDmOrmEE4pZ6NQifOr7We5S', status='error'), 
#       ToolMessage(content='finance data saved to data\\session_tmp\\finance_data.csv', name='fetch_financial_data', id='0459dcb0-b797-48b3-8be9-1bfe0f884f0d', tool_call_id='call_fzob2lqGhp5T8tROS20sNA75'), 
#       ToolMessage(content='{"web_search_result": {"query": "recent news about \'삼성전자\'", "follow_up_questions": null, "answer": null, "images": [], "results": [{"title": "Samsung Global Newsroom - All the latest news, key facts and inspiring ...", "url": "https://news.samsung.com/global/", "content": "[Interview] Exploring the World Through a Lens: Steve McCurry x Samsung Art Store\\non December 29, 2023\\nPress Release\\nSamsung Electronics To Unveil New Vacuum Lineup That Redefines Home Cleaning With Enhanced AI at CES 2024\\nKorea on December 28, 2023\\nAROUND THE WORLD\\nVietnam\\nSamsung Receives Four Awards at Editors’ Choice Awards 2023\\nChile\\nSamsung’s The Wall Installed at Aninat Gallery\\nMalaysia\\nSamsung Named Recipient of CXP Best Customer Experience Awards 2023\\nPoland\\nSamsung Electronics Poland Wins ‘Employer of Tomorrow’ Competition\\nPoland\\nSamsung Wins Most Votes at Tech Awards 2023 in Poland\\nLATEST\\nVideo\\nRecommended\\nCES 2024\\nSamsung Art Store\\nHome Appliance Core Tech\\nGalaxy Wearable\\nMedia Library\\nCES 2024\\nIFA 2023\\nGalaxy Z Fold5│Flip5\\nBespoke Life 2023\\nBelieve in People, Believe in Change.\\n Opening a New Era of Mobile AI\\nKorea on January 1, 2024\\nPress Release\\nSamsung Electronics Expands Odyssey Gaming Monitor Lineup With New OLED Models at CES 2024\\nKorea on January 3, 2024\\nPress Release\\nSamsung to Exhibit More C-Lab Startups Than Ever Before at CES 2024\\nKorea on December 28, 2023\\n Top Stories\\nCES 2024\\nAI for All\\nGalaxy Z Flip5 | Z Fold5\\nJoin the Flip Side\\nReduce, Reuse, Upcycle\\nFor a Sustainable Earth\\n6G Networks\\nNext Hyper-Connected\\n[Invitation] RSS Feed\\nGet daily updates from Samsung Newsroom\\nSAMSUNG\\nCopyright© 2010-2024 SAMSUNG All Rights Reserved.\\n Samsung Global Newsroom – All the latest news, key facts and inspiring stories about Samsung Electronics.\\n", "score": 0.74385756, "raw_content": null}, {"title": "Samsung U.S. Newsroom | Latest News & inspiring stories about Samsung ...", "url": "https://news.samsung.com/us/", "content": "the Formula 1 Heineken Silver Las Vegas Grand Prix w...\\nSamsung Lights Up the Formula 1 Heineken Silver Las Vegas Grand Prix with the World’s First 481-Foot F1 Logo Rooftop LED Display\\n11.17.23\\n‘Lost and Found’ Just Got an Upgrade: A Conversation With the Make...\\n‘Lost and Found’ Just Got an Upgrade: A Conversation With the Makers of the Galaxy SmartTag2\\n11.16.23\\nSamsung Press Conference at CES 2024 ‘AI for All: Connectivity i...\\nSamsung Press Conference at CES 2024 ‘AI for All: Connectivity in the Age of AI’\\n12.06.23\\n300 State Finalists Shine in Samsung Solve for Tomorrow STEM Competiti...\\n300 State Finalists Shine in Samsung Solve for Tomorrow STEM Competition, Nearing $100,000 Prize Potential\\n12.05.23\\nSmartThings Partners with Eve Systems to Revolutionize Home Energy Man...\\nSmartThings Partners with Eve Systems to Revolutionize Home Energy Management\\n12.04.23\\nBring Home the Holiday Cheer with up to 35% Off Samsung Tech...\\nBring Home the Holiday Cheer with up to 35% Off Samsung Tech\\n11.29.23\\nSamsung Holiday Savings to Help You Tech the Halls: Cyber Monday Deals...\\nSamsung Holiday Savings to Help You Tech the Halls: Cyber Monday Deals\\n11.27.23\\nRain or Shine: Samsung Upholds Veterans Day Tradition...\\nRain or Shine: Samsung Upholds Veterans Day Tradition\\n11.22.23\\nSamsung Electronics Ranked as a Top Five Best Global Brand for the Fou...\\nSamsung Electronics Ranked as a Top Five Best Global Brand for the Fourth Consecutive Year\\n11.21.23\\nSamsung Recognized for Reinventing the Future by Consumer Technology A...\\nSamsung Recognized for Reinventing the Future by Consumer Technology Association\\n11.15.23\\n3 Ways to Discard and Reuse Old Devices How Samsung Has Led Innovations in Digital Signage for 14 Years\\n12.05.23\\nSmartThings Partners with Eve Systems to Revolutionize Home Energy Man...\\nSmartThings Partners with Eve Systems to Revolutionize Home Energy Management\\n12.04.23\\nMore Than a Gesture: How Galaxy Watch’s Universal Gestures Featu...\\nMore Than a Gesture: How Galaxy Watch’s Universal Gestures Feature Enhances Accessibility\\n12.03.23\\nSamsung Brings Legendary Artist Keith Haring Collection to The Frame...\\nSamsung Brings Legendary Artist Keith Haring Collection to The Frame\\n11.30.23\\nBring Home the Holiday Cheer with up to 35% Off Samsung Tech...\\n Featured News\\nSolve for Tomorrow Names State Finalists\\nFeatured News\\nHow Samsung Has Led Innovations in Digital Signage for 14 Years\\n12.5.2023\\nMore Than a Gesture: How Galaxy Watch’s Universal Gestures Feature Enhances Accessibility\\n12.3.2023\\nSamsung Brings Legendary Artist Keith Haring Collection to The Frame\\n11.30.2023\\nLatest News\\nSamsung Press Conference at CES 2024 ‘AI for All: Connectivity i...\\nSamsung Press Conference at CES 2024 ‘AI for All: Connectivity in the Age of AI’\\n Bring Home the Holiday Cheer with up to 35% Off Samsung Tech\\n11.29.23\\nSamsung Galaxy Named Official Tablet Partner of Big Ten Conference...\\nSamsung Galaxy Named Official Tablet Partner of Big Ten Conference\\n11.28.23\\nSamsung Holiday Savings to Help You Tech the Halls: Cyber Monday Deals...\\nSamsung Holiday Savings to Help You Tech the Halls: Cyber Monday Deals\\n11.27.23\\nSamsung Lights Up This Holiday Gifting Season fr...\\n3 Ways to Discard and Reuse Old Devices This Holiday Gifting Season from Samsung Care\\n11.14.23\\nMedia Library\\nEvents\\nGalaxy Unpacked 2023\\nSDC23\\nSamsung Solve for Tomorrow\\nSign Up for the Latest Samsung News & Announcements\\nGet Press Releases & Latest News as it Develops!\\n", "score": 0.71113056, "raw_content": null}, {"title": "반도체 성적표 나온다…삼성전자, 3분기 확정 실적 공개", "url": "https://www.newsis.com/view/NISX20241030_0002940344", "content": "-26665초 전 > [속보]공수처 \\"윤 대통령 측 현장조사 등 일체 거부해 조사 불발\\" -8367초 전 > [속보]공수처, 윤 대통령 3차 강제구인 위해 서울구치소 도착 -3455초 전 > [속보]오동운 공수처장 \\"오늘 중 대통령 강제구인 다시 나설 것\\" -558초 전 > [속보]트럼프 \\"내달 1일부터 中에 10% 관세부과 검토\\" 1시간 전 > [속보] 넷플릭스, 4분기 \'호실적\' 발표…구독자 3억 명 돌파 [서울=뉴시스] 홍효식 기자 = 삼성전자가 2024년 3분기 잠정실적을 발표한 8일 서울 삼성전자 서초사옥 모습.삼성전자는 이날 개장 전 잠정실적 발표를 통해 전년 동기 대비 매출은 17.21% 증가한 79조원, 영업이익은 274.49% 늘어난 9조1000억원을 기록했다고 공시했다. 삼성전자는 3분기 잠정실적 공시 직후 이례적으로 설명자료를 내고 \\"DS(반도체)는 인센티브 충당 등 일회성 비용 영향으로 전분기 대비 실적이 하락했다\\"고 밝혔다.", "score": 0.63125396, "raw_content": null}, {"title": "Latest - Samsung Global Newsroom", "url": "https://news.samsung.com/global/latest", "content": "Daily updated news, interviews, infographics and more", "score": 0.57408494, "raw_content": null}, {"title": "삼성전자 Cfo \\"지금 이슈는 성장의 기회…반드시 단시간내 해결\\" (종합) | 연합뉴스", "url": "https://www.yna.co.kr/view/AKR20250131047401003", "content": "삼성전자 CFO \\"지금 이슈는 성장의 기회…반드시 단시간내 해결\\"(종합) | 연합뉴스 영상 삼성전자 CFO \\"지금 이슈는 성장의 기회…반드시 단시간내 해결\\"(종합) 삼성전자 CFO \\"지금 이슈는 성장의 기회…반드시 단시간내 해결\\"(종합) 박순철 삼성전자 신임 최고재무책임자는 31일 \\"다양한 사업 포트폴리오와 주요 사업의 경쟁력을 바탕으로 현재 이슈는 점차 회복할 수 있을 것\\"이라며 \\"반드시 짧은 시간 내에 해결할 수 있다\\"고 말했다. 박 CFO는 삼성전자 미래전략실 출신으로, 지난해 연말 인사에서 삼성전자의 새 \'곳간지기\'를 맡았으며 이날 처음으로 실적 콘퍼런스콜에 나섰다. (서울=연합뉴스) 장하나 한지은 기자 = 박순철 삼성전자 신임 최고재무책임자(CFO)는 31일 \\"다양한 사업 포트폴리오와 주요 사업의 경쟁력을 바탕으로 현재 이슈는 점차 회복할 수 있을 것\\"이라며 \\"반드시 짧은 시간 내에 해결할 수 있다\\"고 말했다. 박 CFO는 삼성전자 미래전략실(미전실) 출신으로, 지난해 연말 인사에서 삼성전자의 새 \'곳간지기\'를 맡았으며 이날 처음으로 실적 콘퍼런스콜에 나섰다. 영상 영상", "score": 0.45289946, "raw_content": null}], "response_time": 1.45}, "source": ["https://news.samsung.com/global/", "https://news.samsung.com/global/latest", "https://news.samsung.com/us/", "https://www.newsis.com/view/NISX20241030_0002940344", "https://www.yna.co.kr/view/AKR20250131047401003"]}', name='fetch_company_news', id='28abc904-549c-4b52-b52d-688beca0029d', tool_call_id='call_vaXBlOlBxXaCoO5tAa2v0mb7')
#   ]
#  }
# }
# {'agent': 
#  {'messages': 
#   [
#       AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_K1PUeEmDbRNI7HMWriCx8jX8', 'function': {'arguments': '{"query":"2024년 삼성전자의 주식 동향 분석","data_path":"data\\\\session_tmp\\\\stock_data.csv"}', 'name': 'analyze_csv_data'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 39, 'prompt_tokens': 5197, 'total_tokens': 5236, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-2024-08-06', 'system_fingerprint': 'fp_4691090a87', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-3f2b8c47-1c00-422d-beb4-ab65b15d6d99-0', tool_calls=[{'name': 'analyze_csv_data', 'args': {'query': '2024년 삼성전자의 주식 동향 분석', 'data_path': 'data\\session_tmp\\stock_data.csv'}, 'id': 'call_K1PUeEmDbRNI7HMWriCx8jX8', 'type': 'tool_call'}], usage_metadata={'input_tokens': 5197, 'output_tokens': 39, 'total_tokens': 5236, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})
#   ]
#  }
# }
# {'tools': 
#  {'messages': 
#   [
#       ToolMessage(content='{"input": "2024년 삼성전자의 주식 동향 분석", "output": "삼성전자의 2024년 주식 동향에 대한 초기 데이터를 분석한 결과는 다음과 같습니다:\\n\\n1. **평균 주가**: 75,626.12 원\\n2. **주가의 표준편차**: 1,294.14 원\\n3. **최소 주가**: 74,882.2 원\\n4. **1사분위수 (Q1)**: 74,980.1 원\\n5. **중앙값 (Q2, 50%)**: 74,980.1 원\\n6. **3사분위수 (Q3)**: 75,371.6 원\\n7. **최대 주가**: 77,916.6 원\\n\\n이 데이터를 통해 삼성전자의 주가는 2024년 1월 초에 비교적 안정된 범위 내에서 움직이고 있으며, 평균적으로 75,626.12 원 수준을 기록했습니다. 표준편차가 약 1,294.14 원으로, 주가의 변동성이 어느 정도 존재함을 나타냅니다. \\n\\n주가가 가장 높았던 날은 77,916.6 원을 기록했으며, 가장 낮았던 날은 74,882.2 원이었습니다. 중앙값과 1사분위수가 같아, 데이터의 절반이 이 값 이하에 위치하고 있음을 알 수 있습니다. \\n\\n향후 주가 동향을 예측하기 위해 추가적인 데이터 분석이 필요할 것입니다."}', name='analyze_csv_data', id='feb65bbc-b283-4032-92b6-a57c7682b1d7', tool_call_id='call_K1PUeEmDbRNI7HMWriCx8jX8')
#   ]
#  }
# }
# {'agent': 
#  {'messages': 
#   [
#       AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_tUyyKg0EfrGdx2y1vMQv7ZOJ', 'function': {'arguments': '{"query":"2024년 삼성전자의 재무 상태 분석","data_path":"data\\\\session_tmp\\\\finance_data.csv"}', 'name': 'analyze_csv_data'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 5594, 'total_tokens': 5632, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 5120}}, 'model_name': 'gpt-4o-2024-08-06', 'system_fingerprint': 'fp_4691090a87', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-8303af2a-cad9-4248-a79d-946143352f5e-0', tool_calls=[{'name': 'analyze_csv_data', 'args': {'query': '2024년 삼성전자의 재무 상태 분석', 'data_path': 'data\\session_tmp\\finance_data.csv'}, 'id': 'call_tUyyKg0EfrGdx2y1vMQv7ZOJ', 'type': 'tool_call'}], usage_metadata={'input_tokens': 5594, 'output_tokens': 38, 'total_tokens': 5632, 'input_token_details': {'audio': 0, 'cache_read': 5120}, 'output_token_details': {'audio': 0, 'reasoning': 0}})
#   ]
#  }
# }
# {'tools': 
#  {'messages': 
#   [
#       ToolMessage(content='{"input": "2024년 삼성전자의 재무 상태 분석", "output": "주어진 데이터는 삼성전자의 2024년 재무상태표 일부인 것 같습니다. 주요한 항목을 분석해보겠습니다.\\n\\n### 주어진 데이터 요약:\\n1. **자산총계 (Total Assets)**\\n   - 제 56 기 반기말: 485,758,000,000,000 원\\n   - 제 55 기말: 455,906,000,000,000 원\\n   - 자산이 증가했습니다.\\n\\n2. **유동자산 (Current Assets)**\\n   - 제 56 기 반기말: 217,858,000,000,000 원\\n   - 제 55 기말: 195,937,000,000,000 원\\n   - 유동자산이 증가했습니다.\\n\\n3. **미수금 (Short-Term Other Receivables)**\\n   - 제 56 기 반기말: 7,729,560,000,000 원\\n   - 제 55 기말: 6,633,250,000,000 원\\n   - 미수금이 증가했습니다.\\n\\n4. **선급비용 (Short-Term Prepaid Expenses)**\\n   - 제 56 기 반기말: 3,769,460,000,000 원\\n   - 제 55 기말: 3,366,130,000,000 원\\n   - 선급비용이 증가했습니다.\\n\\n5. **현금및현금성자산 (Cash and Cash Equivalents)**\\n   - 제 56 기 반기말: 49,844,400,000,000 원\\n   - 제 55 기말: 69,080,900,000,000 원\\n   - 현금및현금성자산이 감소했습니다.\\n\\n### 분석:\\n- **자산 증가**: 전체 자산과 유동자산이 증가한 것은 긍정적인 신호로, 회사의 자산규모가 커졌다는 것을 의미합니다.\\n- **현금 감소**: 현금및현금성자산이 감소한 것은 주의가 필요합니다. 이는 회사가 투자나 부채 상환 등으로 현금을 사용했을 가능성을 시사합니다.\\n- **미수금 및 선급비용 증가**: 이는 자산 중 일부가 미수금이나 선급비용 형태로 유지되고 있음을 보여줍니다. 이는 단기적으로 자금 회전에 영향을 미칠 수 있습니다.\\n\\n이 데이터를 바탕으로 삼성전자의 2024년 반기 재무 상태는 자산의 증가와 함께 일부 현금의 감소가 관찰되며, 이는 회사의 전략적 재무 운영과 관련이 있을 수 있습니다. 보다 정확한 해석은 추가적인 데이터를 참고할 필요가 있습니다."}', name='analyze_csv_data', id='c7d459b9-cb8b-4dbf-b5de-8dd53d4e8601', tool_call_id='call_tUyyKg0EfrGdx2y1vMQv7ZOJ')
#   ]
#  }
# }