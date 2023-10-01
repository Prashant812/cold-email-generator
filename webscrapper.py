import openai as ai
import os
import streamlit as st
from langchain.docstore.document import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain.utilities import ApifyWrapper

os.environ["OPENAI_API_KEY"] = st.secrets["openai_key"]
os.environ["APIFY_API_TOKEN"] = st.secrets["apify_key"]



def scrapper(url_link):
    apify = ApifyWrapper()
    # Call the Actor to obtain text from the crawled webpages
    loader = apify.call_actor(
        actor_id="apify/website-content-crawler",
        run_input={"startUrls": [{"url": url_link}]},
        dataset_mapping_function=lambda item: Document(
            page_content=item["text"] or "", metadata={"source": item["url"]}
        ),
    )

    # Create a vector store based on the crawled data
    index = VectorstoreIndexCreator().from_loaders([loader])
    result = index.query("Extract all the content in text format")

    return result


#test_1 = scrapper("https://www.exlservice.com/about-exl")
#print(test_1)