from langchain_community.retrievers import TFIDFRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from django_ai_assistant import AIAssistant
from rag.models import DjangoDocPage


class DjangoDocsAssistant(AIAssistant):
    id = "django_docs_assistant"  # noqa: A003
    name = "Django Docs Assistant"
    instructions = (
        "You are an assistant for answering questions related to Django web framework. "
        "Use the following pieces of retrieved context from Django's documentation to answer "
        "the user's question. If you don't know the answer, say that you don't know. "
        "Use three sentences maximum and keep the answer concise."
    )
    model = "gpt-4o-mini"
    has_rag = True

    def get_retriever(self) -> BaseRetriever:
        # NOTE: on a production application, you should persist or cache the retriever,
        # updating it only when documents change.
        docs = (page.as_langchain_document() for page in DjangoDocPage.objects.all())
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        return TFIDFRetriever.from_documents(splits)
