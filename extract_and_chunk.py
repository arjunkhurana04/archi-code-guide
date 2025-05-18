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

    def _is_point_in_polygon(self, point, polygon):
        """
        Check if a point is inside a polygon using ray casting algorithm.
        
        :param point: (x, y) tuple representing the point
        :param polygon: List of Points defining the polygon
        :return: True if the point is inside the polygon, False otherwise
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0].x, polygon[0].y
        for i in range(n + 1):
            p2x, p2y = polygon[i % n].x, polygon[i % n].y
            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
    
    def _is_paragraph_in_table(self, paragraph_bounding_regions, table_polygons):
        """
        Check if a paragraph is contained within any table.
        """

        centre_line = paragraph_bounding_regions[len(paragraph_bounding_regions)//2]
        line_polygon = centre_line.polygon 
        center_x = sum(point.x for point in line_polygon) / len(line_polygon)
        center_y = sum(point.y for point in line_polygon) / len(line_polygon)
        

        center_point = (center_x, center_y)
        
        for table_polygon in table_polygons:
            if self._is_point_in_polygon(center_point, table_polygon):
                return True
                
        return False

    def process_pdf(self, pdf_path: str):
        """
        Process a PDF file from the data folder to extract text, tables, and other data, and chunk the extracted text with paragraphs being the chunks.
        Excludes paras that are contained within tables.

        :param pdf_filename: Name of the PDF file in the data folder.
        :return: A dictionary containing extracted text, tables, and chunked text.
        """

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        with open(pdf_path, "rb") as pdf_file:
            poller = self.client.begin_analyze_document("prebuilt-document", document=pdf_file)
            result = poller.result()

        # return result
    
        extracted_paragraphs_contents = []
        tables = []
        table_polygons = []

        # First, extract table regions
        for table in result.tables:
            table_data = []
            for cell in table.cells:
                table_data.append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": cell.content
                })
            tables.append(table_data)
            
            # Save the table's bounding polygon for later comparison
            if hasattr(table, 'bounding_regions') and table.bounding_regions:
                for region in table.bounding_regions:
                    if hasattr(region, 'polygon'):
                        table_polygons.append(region.polygon)
        
        # Extract text from paras that are not in tables
        extracted_paragraphs = []
        i = 0
        for paragraph in result.paragraphs:
            # Skip paras that are within table regions
            if not self._is_paragraph_in_table(paragraph.bounding_regions, table_polygons):
                extracted_paragraphs_contents.append(paragraph.content)
                extracted_paragraphs.append(paragraph)

        def convert_table_to_markdown(table_data):
            """
            Convert a table from Azure Document Intelligence format to Markdown.
            
            Args:
                table_data (list): List of dictionary items representing table cells,
                                each with 'row_index', 'column_index', and 'content' keys.
            
            Returns:
                str: Markdown representation of the table
            """
            from collections import defaultdict
            
            # Step 1: Organize cells by row and column
            rows_dict = defaultdict(dict)
            max_col = 0
            max_row = 0
            
            for cell in table_data:
                row = cell['row_index']
                col = cell['column_index']
                content = cell['content'].strip()
                rows_dict[row][col] = content
                max_col = max(max_col, col)
                max_row = max(max_row, row)
            
            # Step 2: Convert to list of rows
            table_rows = []
            for row_index in range(max_row + 1):
                row = []
                for col_index in range(max_col + 1):
                    cell_content = rows_dict[row_index].get(col_index, "")
                    row.append(cell_content)
                table_rows.append(row)
            
            # Step 3: Build Markdown
            def row_to_md(row):
                return "| " + " | ".join(row) + " |"
            
            markdown_output = []
            markdown_output.append(row_to_md(table_rows[0]))  # Header row
            markdown_output.append("|" + " --- |" * len(table_rows[0]))  # Separator
            for row in table_rows[1:]:
                markdown_output.append(row_to_md(row))
            
            markdown_table = "\n".join(markdown_output)
            return markdown_table

        page_numbers = []

        for i in extracted_paragraphs:
            if i.role == "pageNumber":
                page_numbers.append(int(i.content))
            else:
                page_numbers.append(-1)
        
        def replace_with_nearest_positive(arr):
            # Right-to-left pass
            last = -1
            for i in range(len(arr)-1, -1, -1): last = arr[i] = arr[i] if arr[i] != -1 else last
            
            # Handle trailing -1s with leftmost non-negative number
            last = next((x for x in arr if x != -1), -1)
            for i in range(len(arr)): arr[i] = last if arr[i] == -1 else arr[i]
            
            return arr
        
        
        page_numbers = replace_with_nearest_positive(page_numbers)
        metadatas = [f"Page {i}" for i in page_numbers] + [f"Table: {i+1}" for i in range(len(result.tables))]

        chunks = extracted_paragraphs_contents + [convert_table_to_markdown(i)  for i in tables]

        return {
            "text": "\n".join(extracted_paragraphs_contents),
            "tables": tables,
            "chunks": chunks,
            "metadatas": metadatas,
        }