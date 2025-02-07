# FinPilot LLM Application

## LLM Application API Server Using `LangGraph` and `FastAPI`
Welcome to the FinPilot API Server repository. This project is designed to enhance the efficiency of business document creation by providing a real-time document drafting assistant for use within Google Docs. It integrates a custom-built Chrome extension and FinPilot, an LLM application powered by LangGraph, offering features such as automated draft creation, content generation, and data analysis.

<br>

## 1. Key Features

This application offers essential capabilities for writing and managing business documents:

1. **Draft Document Creation**: Automatically generate structured drafts based on user input, saving time.
2. **Paragraph Generation and Expansion**: Generate new paragraphs based on PDFs or the latest web data to enhance documents.
3. **Summary and Expansion**: Summarize or expand documents to adjust length as needed.
4. **Web Data Collection and Analysis**: Collect real-time data from the web and provide visual insights.
5. **File Upload-Based Data Analysis**: Upload CSV files for automatic analysis and visualization.

<br>

## 2. Architecture Overview

The project uses LangGraph to provide document processing and language model functionality, interacting with the custom Chrome extension via a FastAPI server. Its flexible API design and real-time data processing deliver high-performance document support.

### 2-1. Key Components:
- **LLM Processing Layer**: Core processing engine powered by LangGraph for complex NLP tasks.
- **FastAPI Server**: Delivers fast and reliable API services.

<br>

## 3. Getting Started

### 3-1. Prerequisites

Before starting, ensure you have the following:
- Python 3.10 or higher
- FastAPI installed
- LangGraph and other dependencies listed in `requirements.txt`

### 3-2. Installation and Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN05-FINAL-3TEAM.git
    cd SKN05-FINAL-3TEAM/async_singleton_server
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables by configuring the following API keys in `config/secret_keys.py`:
    ```python
    OPENAI_API_KEY = 'your-openai-api-key'
    TAVILY_API_KEY = 'your-tavily-api-key'
    USER_AGENT = 'your-user-agent-string'
    DART_API_KEY = 'your-dart-api-key'
    LANGSMITH_API_KEY = 'your-langsmith-api-key'
    LANGSMITH_TRACING = 'true'
    LANGSMITH_ENDPOINT = 'https://api.smith.langchain.com'
    LANGSMITH_PROJECT = 'your-langsmith-project-name'
    ```

4. Run the server:
    ```bash
    python app.py
    ```

### 3-3. Chrome Extension Integration
The Chrome extension for Google Docs integration is maintained in a separate folder (`front-end/`). Follow the installation instructions there to connect it to the API server.

<br>

## 4. API Endpoints

### 4-1. Key Endpoint Descriptions:

| Endpoint        | Method | Description                                                  |
|-----------------|--------|--------------------------------------------------------------|
| `/query`        | POST   | Invokes the FinPilot LangGraph Application based on user input. |
| `/pdfs/upload`  | POST   | Uploads a PDF file for use in paragraph generation.          |
| `/csvs/upload`  | POST   | Uploads a CSV file for data visualization and analysis.      |
| `/pdfs/delete`  | POST   | Deletes uploaded PDF content from the vector database.       |
| `/csvs/delete`  | POST   | Deletes uploaded CSV files.                                  |

While the server is running, detailed API documentation can be found at [Test](http://localhost:8000/docs).

<br>

## 5. FinPilot Application

### 5-1. Key Processes:

#### 5-1-1. 'Draft Creation'
Generates a draft of the desired document. FinPilot emulates the human document creation process by organizing sections and filling in content. It gathers relevant data such as stock reports, financial statements, and news, which it analyzes to generate a draft. Each draft typically takes 2–6 minutes to generate and spans 5–10 Google Docs pages.
- **Usage** at [Test](http://localhost:8000/docs)
```
example:
-------------------------------------------------
{
    "session_id": "session-1",
    "question": "삼성전자 기업분석 보고서 초안 작성해줘.",
    "chat_option": "초안 작성"
}
```

#### 5-1-2. 'Paragraph Generation'
Generates paragraphs on specific topics or to enhance existing documents. Uploading a PDF provides FinPilot with contextually relevant content. If no PDF is available, it conducts web searches and generates paragraphs using the Self-RAG and Corrective RAG architectures.
- **Usage** at [Test](http://localhost:8000/docs)
```
example:
-------------------------------------------------
{
    "session_id": "session-1",
    "question": "최근 코스피 시장 이슈를 정리해서 인사이트를 작성해줘.",
    "chat_option": "단락 생성"
}
```

#### 5-1-3. 'Summary/Expansion'
Quickly summarizes or expands specific sections of a document. This functionality optimizes document length without compromising content quality.
- **Usage** at [Test](http://localhost:8000/docs)
```
example:
-------------------------------------------------
{
    "session_id": "session-1",
    "question": "~~~~~~~~~~~~ 이 문장 분량을 늘려줘",
    "chat_option": "요약 / 확장"
}
```

#### 5-1-4. 'Data Visualization (Web)'
Analyzes and visualizes data based on web search results. FinPilot generates Python code to create graphs and charts reflecting the collected data.
- **Usage** at [Test](http://localhost:8000/docs)
```
example:
-------------------------------------------------
{
    "session_id": "session-1",
    "question": "최근 5개년 미국 GDP 그래프 그려줘.",
    "chat_option": "데이터 시각화 (Web)"
}
```

#### 5-1-5. 'Data Visualization (Upload)'
Analyzes and visualizes user-uploaded CSV data using Python-generated charts. FinPilot processes the data with Pandas and creates various visual representations.
- **Usage** at [Test](http://localhost:8000/docs)
```
example:
-------------------------------------------------
{
    "session_id": "session-1",
    "question": "주어진 데이터를 다양한 관점에서 분석하고 시각화 해줘",
    "chat_option": "데이터 시각화 (Upload)"
}
```

<br>

## 6. Project Structure

### 6-1. FinPilot API Server Structure (`async_singleton_server/`)

```
├── app.py                         # Main application initialization
├── charts/                        # Temp directory for saving charts
├── config/                        # Configuration files and API settings
├── data/                          # Temporary directory for CSV file storage
├── finpilot/                      # FinPilot application modules
│   ├── core.py                    # Initialize the FinPilot LLM application
│   ├── draft.py                   # Draft generation logic
│   ├── length_control.py          # Summary and expansion logic
│   ├── memory.py                  # Memory management for LangGraph
│   ├── paragraph.py               # Paragraph creation logic
│   ├── request_model.py           # API input models
│   ├── router.py                  # LangGraph node routing logic
│   ├── utils.py                   # Utility functions
│   ├── vectorstore.py             # Vector storage management for RAG
│   ├── visualize_upload_data.py   # Visualization logic for uploaded data
│   └── visualize_web_data.py      # Web data analysis and visualization
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── CORPCODE.xml                   # Corporate codes for fetching stock data
└── README.md                      # Project documentation
```

<br>

## 7. License

This project is open-source software licensed under the [MIT License](LICENSE).

<br>

## 8. Contact and Support
For any questions or support, please contact [martinus.choi@gmail.com](mailto:martinus.choi@gmail.com), and we will respond promptly.

