import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFProcessor:
    def __init__(self, azure_endpoint: str, azure_key: str, chunk_size: int = 1000, chunk_overlap: int = 100):
        """
        Initialize the PDFProcessor with Azure Document Intelligence credentials and chunking parameters.

        :param azure_endpoint: Azure Form Recognizer endpoint.
        :param azure_key: Azure Form Recognizer API key.
        :param chunk_size: Size of each text chunk.
        :param chunk_overlap: Overlap between consecutive chunks.
        """
        self.client = DocumentAnalysisClient(endpoint=azure_endpoint, credential=AzureKeyCredential(azure_key))
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process_pdf(self, pdf_path: str):
        """
        Process a PDF file from the data folder to extract text, tables, and other data, and chunk the extracted text.

        :param pdf_filename: Name of the PDF file in the data folder.
        :return: A dictionary containing extracted text, tables, and chunked text.
        """

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        with open(pdf_path, "rb") as pdf_file:
            poller = self.client.begin_analyze_document("prebuilt-document", document=pdf_file)
            result = poller.result()

        
        extracted_text = []
        tables = []

        # Extract text
        for page in result.pages:
            for line in page.lines:
                extracted_text.append(line.content)

        # Extract tables
        for table in result.tables:
            table_data = []
            for cell in table.cells:
                table_data.append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": cell.content
                })
            tables.append(table_data)

        # Combine all text into a single string
        full_text = "\n".join(extracted_text)

        # Chunk the text
        chunks = self.text_splitter.split_text(full_text)

        return {
            "text": full_text,
            "tables": tables,
            "chunks": chunks
        }