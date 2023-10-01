from urllib.parse import urlparse
from langchain.chat_models import ChatOpenAI
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain, BaseCombineDocumentsChain
from langchain.tools.base import BaseTool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import Field
import os, asyncio,trafilatura
from langchain.docstore.document import Document
import requests


def get_url_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def _get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap  = 20,
        length_function = len,
    )

class WebpageQATool(BaseTool):
    name = "query_webpage"
    description = "Browse a webpage and retrieve the information"
    text_splitter: RecursiveCharacterTextSplitter = Field(default_factory=_get_text_splitter)
    qa_chain: BaseCombineDocumentsChain

    def _run(self, url: str, question: str) -> str:
        response = requests.get(url)
        page_content = response.text
        print(page_content)
        docs = [Document(page_content=page_content, metadata={"source": url})]
        web_docs = self.text_splitter.split_document(docs)
        results = []
        for i in range(0, len(web_docs), 4):
            input_docs = web_docs[i:i+4]
            window_result = self.qa_chain({"input_documents": input_docs, "question": question}, return_only_outputs=True)
            results.append(f"Response from window {i} - {window_result}")
        results_docs = [Document(page_content="\n".join(results), metadata={"source": url})]
        print(results_docs)
        return self.qa_chain({"input_documents": results_docs, "question": question}, return_only_outputs=True)

    async def _arun(self, url: str, question: str) -> str:
        raise NotImplementedError

def run_llm(url, query):
    llm = ChatOpenAI(temperature=0.5)
    query_website_tool = WebpageQATool(qa_chain=load_qa_with_sources_chain(llm))
    result = query_website_tool._run(url, query)  # Pass the URL and query as arguments
    return result

#mission_desc = run_llm('https://www.simhatel.com/', 'Extract the goal of the company')
#print(mission_desc)