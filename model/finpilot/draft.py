from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from datetime import datetime

from tavily import TavilyClient

from typing import List, Annotated
from pydantic import BaseModel
from operator import add

import yfinance as yf
import pandas as pd
import requests
import os



class DraftProcess:
    def __init__(self, data_dir):
        # Web Search API Client
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        # LLM API Client
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, api_key=os.environ["OPENAI_API_KEY"])
        self.data_dir = data_dir


        @tool
        def fetch_stock_data(corp_name:str, start_date:str, end_date:str):
            """
            Use this tool when you need to fetch stock data(주식) of certain company.
            
            Args:
                corp_code (str) : comapy name (ex : '삼성전자')
                start_date (str) : start date about stock data (ex : '2024-01-01')
                end_date (str) : end date about stock data (ex : '2024-12-31')
            
            Returns:
                str : path message about saved file
            """
            def fetch_ticker_list():
                tickers = stock.get_market_ticker_list(market="ALL")

                return {
                    stock.get_market_ticker_name(ticker) : ticker for ticker in tickers
                }

            def search_ticker_by_name(ticker_dict, name):
                return ticker_dict[name]
            
            ticker_dict = fetch_ticker_list()
            stock_code = search_ticker_by_name(ticker_dict, corp_name.replace(" ", ""))

            stock = yf.download(
                stock_code + '.KS', 
                start=start_date, 
                end=end_date, 
                progress=False
            )
            
            df = pd.DataFrame(index = stock.index)
            df[f'{stock_code}'] = stock['Close']
            
            csv_path = data_dir / "stock_data.csv"
            df.to_csv(csv_path)

            return f"Stockfile saved to {os.path.relpath(data_dir / 'stock_data.csv', os.getcwd())}"
        

        @tool
        def fetch_financial_data(corp_name, report_year):
            """
            Use this tool when you need to fetch financial data (재무재표).
            
            Args:
                corp_name (str) : Company name (ex : '삼성전자')
                report_year (str) : Year that data written (ex : 2024)
            
            Returns:
                str : path message about saved file
            """

            url = f"https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

            corp_code_df = pd.read_xml('CORPCODE.xml', encoding='utf-8')
            corp_code = corp_code_df.loc[corp_code_df['corp_name'] == corp_name.replace(" ", ""), 'corp_code'].iloc[0]
            corp_code = str(corp_code).zfill(8)

            params = {
                'crtfc_key': os.getenv('DART_API_KEY'),
                'corp_code': corp_code,
                'bsns_year': report_year,       # 사업연도
                'reprt_code': '11012',     # 보고서 코드 (반기 보고서)
                'fs_div': 'CFS'            # 재무제표 유형 ('CFS' 또는 'OFS') CFS: 연결재무제표 OFS: 재무제표 (개별)
            }

            # API 호출
            response = requests.get(url, params=params)

            # JSON 응답 확인
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '000':
                    df = pd.DataFrame(data['list'])
                    df.to_csv(data_dir / "finance_data.csv", encoding="utf-8")
                    return f"finance data saved to {os.path.relpath(data_dir / 'finance_data.csv', os.getcwd())}"
                else:
                    return f"Cannot find Data for {corp_name}"
            else:
                return f"Fail to Call API, {response.status_code}"
        

        @tool
        def analyze_csv_data(query : str, data_path : str):
            """
            저장된 주식 데이터와 재무 데이터를 pandas_agent로 분석하고 질문에 답변합니다.

            Args : 
                query (str) : 사용자 질문
                data_path (str) : 분석할 csv file 경로
            """

            custom_prefix = f"""
                You are very smart analyst can use given data.
                Please analyze the data in various perspective to fine valuable insight.
                You shoould always make the greatest output with accurate metrics and tables.
            """

            df_list = [pd.read_csv(data_path)]

            pandas_agent = create_pandas_dataframe_agent(
                ChatOpenAI(model="gpt-4o"),
                df_list,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                prefix = custom_prefix # (옵션) prompt에 의도한 문장을 추가
            )

            result = pandas_agent.invoke(query)

            return result

        @tool
        def fetch_company_news(company_name: str) -> str:
            """
            Collect recent news for the given company.
            
            Args :
                company_name : Company name
            """
            search_results = tavily_client.search(query=f"recent news about {company_name}", days=7)
            return f"Collected news and market data for {company_name}: \n{search_results}"

        @tool
        def fetch_market_news(sector: str) -> str:
            """
            Collect recent market datafor the given company's sector.
            
            Args
                sector (str) : company's sector
            """
            search_results = tavily_client.search(query=f"{sector} industry news", days=7)
            return f"Collected news and market data for {sector}: {search_results}"

        @tool
        def fetch_webpages_scrape(urls: List[str]) -> str:
            """Scrape the provided web pages for detailed information."""
            loader = WebBaseLoader(urls)
            docs = loader.load()
            return "\n\n".join(
                [f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
                for doc in docs]
            )
        
        self.tools = [fetch_stock_data, fetch_financial_data, analyze_csv_data, fetch_company_news, fetch_market_news, fetch_webpages_scrape]
        

        ########################## Outliner ##########################
        class OutlineModel(BaseModel):
            outlines : Annotated[List[str], add]

        outliner_llm = llm.with_structured_output(OutlineModel)
        outliner_system_prompt = """
            당신은 훌륭한 분석가 입니다. 당신은 사용자가 요청한 문서 초안에 대해 목차를 만들어야 합니다.
            이를 위해 다음의 지침에 따라 초안의 목차를 작성하세요 :

            <지침>
            1. 사용자가 요청한 문서 초안에 대해 서론-본론-결론의 흐름이 분명하도록 목차를 작성하세요. 서론, 본론, 결론 이라는 단어를 사용할 필요는 없습니다.
            2. 주식, 재무재표, 뉴스, 웹 검색 등의 데이터 수집을 통해 신빙성있는 문서를 작성할 수 있도록 목차를 작성하세요
            3. 목차는 소제목까지 포함하여 최대 10개의 목차까지만 작성하세요.
            4. 가독성을 위해 번호를 반드시 부여하세요.
            </지침>
        """
        outliner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", outliner_system_prompt),
                ("human", """
                    사용자의 요청은 다음과 같습니다. :
                    <요청>
                    사용자 요청 : {question}
                    </요청>
                    
                    이에 따라 문서의 목차를 작성해주세요.
                """
                )
            ]
        )

        self.outliner = outliner_prompt | outliner_llm



        ########################## Paragraph Writer ##########################
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.paragraph_writer = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.environ["OPENAI_API_KEY"])
        


    def make_outline_node(self, state):
        question = state["question"]

        response = self.outliner.invoke({"question" : question})

        state["outlines"] = response.outlines

        print("[Graph Log] Created outlines :")
        print(f"{state['outlines']}")

        return state
    
    def write_draft_paragraph_node(self, state) :
        question = state["question"]
        outlines = state["outlines"]

        for outline in outlines:
            print(f"[Graph Log] Current Outline Title : {outline}")

            draft_prompt = f"""
                오늘은 {self.today} 입니다.
                당신은 훌륭한 분석가 입니다. 당신은 사용자가 요청한 문서의 초안을 작성해야합니다.
                이를 위해 다음의 지침에 따라 초안의 목차에 대한 단락을 최신 정보를 활용하여 작성하세요 :
                
                <지침>
                1. 사용자의 요청에 대해 현재 주어진 목차에 대한 단락을 작성하세요.
                2. 단락 작성 간 필요한 경우 특정 기업에 대한 '주식', '재무재표' 데이터를 수집하세요.
                3. 특정 기업에 대한 '주식', '재무재표' 데이터를 수집이 필요하지 않은 경우, 뉴스와 웹 검색 만을 사용하여 단락을 작성해세요.
                3. 단락 작성 간 충분한 근거를 제시하며 사실에 입각한 내용을 작성하세요.
                4. 형식은 마크다운, 언어는 한국어를 사용하세요.
                </지침>

                사용자 요청과 현재 작성해야할 목차는 다음과 같습니다. :
                <요청과 목차>
                사용자 요청 : {question}
                현재 목차 : {outline}
                </요청과 목차>

                주식, 재무재표 데이터를 수집하기 위해 제공한 tools를 사용하며 해당 tool을 사용하면 아래의 경로에 데이터를 저장합니다.
                해당 경로의 데이터를 활용하여 데이터를 분석하세요.
                <데이터 출처>
                주식 데이터 : {os.path.relpath(self.data_dir / 'stock_data.csv', os.getcwd())}
                재무재표 데이터 : {os.path.relpath(self.data_dir / 'finance_data.csv', os.getcwd())}
                </데이터 출처>
            """

            draft_writer = create_react_agent(
                model=self.paragraph_writer,
                tools=self.tools,
                state_modifier = draft_prompt
            )

            response = draft_writer.invoke(state)

            state["messages"] = response["messages"]
            content = ("\n" + response["messages"][-1].content)
            print(f'[Graph Log] current contents : {content}')
            try :
                state["generation"] += content
            except :
                state["generation"] = content
        
        return state