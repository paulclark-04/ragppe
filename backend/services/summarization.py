from services.rag import rag_service
from llama_index.llms.ollama import Ollama
from config import settings
import logging

# Logic ported from user snippet (server.py)

def build_prompt(retrieved_knowledge, threshold):
    context_lines = []
    # retrieved_knowledge is a list of tuples (chunk_text, score)
    for i, (chunk, score) in enumerate(retrieved_knowledge):
        # We don't have metadata id yet, so we use index
        cid = f"result-{i}" 
        context_lines.append(f"[{cid}] (score {score:.2f}) {chunk}")
    context_block = '\n'.join(context_lines)

    instruction_prompt = (
        "Tu es un assistant pédagogique ECE Paris. RÈGLES STRICTES (INTERDICTION ABSOLUE DE LES ENFREINDRE):\n\n"
        
        "✅ CE QUE TU DOIS FAIRE:\n"
        "1. Réponds UNIQUEMENT en français clair et concis\n"
        "2. Utilise EXCLUSIVEMENT les informations textuellement présentes dans les extraits ci-dessous\n"
        "4. Si l'information n'est PAS EXPLICITEMENT dans les extraits, dis EXACTEMENT : "
        "\"Je ne trouve pas cette information dans les documents disponibles.\"\n\n"
        
        "❌ INTERDICTIONS ABSOLUES:\n"
        "1. NE génère JAMAIS de contenu qui n'est pas littéralement dans les extraits\n"
        "2. NE crée AUCUN exemple, équation, code, ou explication de ton propre chef\n"
        "3. NE fais AUCUNE déduction ou inférence au-delà du texte exact\n"
        "4. NE combine PAS d'informations de sources différentes pour créer des faits\n"
        "5. NE réponds JAMAIS si tu n'es pas sûr à 100% que c'est dans les extraits\n"
        
        "⚠️ EN CAS DE DOUTE : Dis que tu ne sais pas. C'est PRÉFÉRABLE à une réponse incertaine.\n\n"
        
        f"EXTRAITS AUTORISÉS (seuil de confiance: {threshold}):\n"
        f"{context_block}\n\n"
        
        "RAPPEL : Si la réponse n'est pas EXPLICITEMENT et CLAIREMENT dans les extraits ci-dessus, "
        "réponds : \"Je ne trouve pas cette information dans les documents disponibles.\""
    )
    return instruction_prompt

async def generate_summary(query: str) -> str:
    # Threshold from snippet
    THRESHOLD = 0.35
    
    # Retrieve relevant chunks with scores
    # rag_service.retrieve now returns [(chunk, score), ...]
    retrieved_results = rag_service.retrieve(query)
    
    # Find best score
    best_score = max((score for _, score in retrieved_results), default=0.0)
    
    if best_score < THRESHOLD:
        return "Information non trouvée dans les sources disponibles."

    # Initialize Ollama
    try:
        llm = Ollama(
            model=settings.OLLAMA_MODEL, 
            base_url=settings.OLLAMA_BASE_URL,
            request_timeout=300.0
        )
    except Exception as e:
        return f"Error initializing Ollama: {str(e)}"
    
    # Construct Prompt using Strict Rules
    system_prompt = build_prompt(retrieved_results, THRESHOLD)
    
    # Final message structure for chat model
    full_prompt = f"{system_prompt}\n\nQuestion User: {query}"
    
    try:
        # Using complete directly
        response = llm.complete(full_prompt)
        return str(response)
    except Exception as e:
        return f"Error generating summary with Ollama: {str(e)}. Ensure Ollama is running locally."
