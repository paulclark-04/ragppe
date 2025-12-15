import os
import shutil
from fastapi import UploadFile
from config import settings

async def ingest_file(file: UploadFile):
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Detect type and route to extraction
    from services.extraction import extract_content
    
    print(f"Ingesting file: {file.filename}, Content-Type: {file.content_type}")
    
    try:
        text_content = await extract_content(file_path, file.content_type)
        print(f"Extraction successful. Text length: {len(text_content)}")
        
        # Index the document
        from services.rag import rag_service
        rag_service.index_document(text_content)
        print("Indexing successful.")
        
        return {
            "filename": file.filename, 
            "status": "processed_and_indexed", 
            "path": file_path,
            "extracted_text_length": len(text_content),
            "preview": text_content[:200]
        }
    except Exception as e:
        print(f"Error during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"filename": file.filename, "status": "error", "error": str(e)}
