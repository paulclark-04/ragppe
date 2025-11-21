# MultiSummarizer - Instructions pour Agents IA

## 🎯 Vue d'ensemble du projet
MultiSummarizer est un assistant IA EdTech pour le résumé multimodal de contenus éducatifs 
(PDF, vidéo, audio, texte). L'objectif est de permettre aux étudiants et professionnels 
de synthétiser rapidement des informations à partir de supports variés.

## 📊 Objectifs SMART
- Traiter 2+ formats (PDF, texte, audio/vidéo) d'ici fin 2025
- Générer des résumés synthétiques (extractifs + abstractifs)
- Interface React/TailwindCSS + base Firebase
- Recherche par mots-clés dans les résumés
- Qualité évaluée via tests utilisateurs (étudiants/enseignants)

## ⚙️ Contraintes techniques
- Conformité RGPD (données éducation)
- Optimisation coûts API et latence
- Modèles open source privilégiés
- Architecture scalable et modulaire

## 🏗️ Architecture RAG cible

### Pipeline de traitement
1. **Ingestion** : Upload fichier → Détection type → Routing
2. **Extraction** :
   - Audio/Vidéo : Whisper (medium/turbo) → transcription
   - PDF : PyMuPDF + Nougat (documents scientifiques) → texte
   - Texte brut : passage direct
3. **Chunking intelligent** :
   - Chunks adaptatifs selon type de document
   - Préservation du contexte business
   - Taille optimale pour fenêtre contexte LLM
4. **Embedding & Indexation** :
   - Transformation en vecteurs (dense embeddings)
   - Stockage dans base vectorielle (FAISS/Pinecone/Milvus)
   - Orchestré par LlamaIndex
5. **Retrieval** :
   - Recherche sémantique (top-k documents)
   - Stratégie hybride : dense (sémantique) + sparse (BM25 pour exact match)
   - Re-ranking par pertinence contextuelle
6. **Génération** :
   - LLM (Mistral Large pour coût/souveraineté, GPT-4/Claude si complexe)
   - Fusion informations texte + visuelles (architecture BridgeNet pour multimodal)
   - Génération résumé + contenus pédagogiques (quiz, flashcards)
7. **Stockage résultats** : Firestore (résumés + métadonnées)

### Stack technique
- **Back-end IA** : Python + FastAPI
- **Frameworks** : LlamaIndex (RAG), LangChain (orchestration), Haystack (production)
- **Modèles** : Whisper, PyMuPDF, Mistral Large, GPT-4, Claude
- **Front-end** : React + TailwindCSS
- **BDD** : Firebase (Firestore + Storage + Auth)
- **Hébergement** : AWS (Lambda pour serverless, EC2 pour GPU)

## 🛠️ Directives de développement RAG

### Principes d'architecture
✅ **Architecture modulaire (microservices)** :
   - Service Auth, Upload, Transcription, Extraction, Embedding, Summarization, Search, API
   - Communication via queues (RabbitMQ/AWS SQS)
   - Conteneurisation Docker + orchestration Kubernetes

✅ **Optimisation du pipeline** :
   - Chunking adaptatif selon type document (académique vs général)
   - Indexation hiérarchique pour requêtes multi-niveaux
   - Retrieval hybride (semantic + keyword)
   - Query expansion automatique via embeddings
   - Feedback loop pour apprentissage continu

✅ **Gestion du contexte** :
   - Contexte maximal : respecter fenêtres LLM (32k-128k tokens selon modèle)
   - Compression contextuelle pour éviter retrieval noise
   - Prompts dynamiques adaptés utilisateur + contexte business
   - Cross-attention mechanisms pour alignement retrieved data ↔ query

### Structure du prompt RAG (à implémenter)
Template prompt RAG optimal
prompt_template = """
Rôle : Tu es un assistant pédagogique expert en synthèse de contenus éducatifs.

Instructions strictes :

- Utilise UNIQUEMENT les informations du contexte fourni ci-dessous
- Si la réponse n'est pas dans le contexte, indique-le clairement
- Ne jamais inventer d'informations
- Cite les sources (extraits de documents) quand pertinent
- Adapte le niveau de détail selon le profil utilisateur (étudiant/enseignant)

Contexte :
{context}

Question utilisateur :
{query}

Réponse (structurée, claire, avec citations) :
"""
### Gestion des embeddings
**Stratégie hybride dense + sparse**
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

**Dense : embeddings sémantiques**
dense_model = SentenceTransformer('all-MiniLM-L6-v2')
dense_embeddings = dense_model.encode(chunks)

**Sparse : BM25 pour mots-clés exacts**
bm25 = BM25Okapi(tokenized_chunks)

**Fusion des résultats (weighted scoring)**
def hybrid_retrieval(query, top_k=5):
dense_scores = semantic_search(query)
sparse_scores = bm25.get_scores(tokenize(query))
combined = 0.7 * dense_scores + 0.3 * sparse_scores
return top_k_results(combined)

### Flux de traitement (code FastAPI)
app/main.py - Structure FastAPI
from fastapi import FastAPI, UploadFile
from services import transcription, extraction, summarization

app = FastAPI()

@app.post("/api/upload")
async def upload_file(file: UploadFile):
# 1. Stockage Firebase Storage
file_url = await storage.save(file)

# 2. Détection type et routing
file_type = detect_type(file)

# 3. Extraction selon type
if file_type == "audio/video":
    text = await transcription.whisper_transcribe(file_url)
elif file_type == "pdf":
    text = await extraction.pymupdf_extract(file_url)
else:
    text = file.read()

# 4. Chunking + Embedding
chunks = chunk_text(text)
embeddings = create_embeddings(chunks)

# 5. Indexation vectorielle
await vector_db.index(embeddings, metadata)

# 6. Génération résumé RAG
summary = await summarization.generate_rag(text, embeddings)

# 7. Stockage résultats
await firestore.save(summary, metadata)

return {"status": "success", "summary_id": summary.id}

### Métriques qualité à implémenter
- **ROUGE scores** (ROUGE-1, ROUGE-2, ROUGE-L) pour résumés texte
- **BLEU scores** pour cohérence
- **Retrieval precision@k** : pertinence top-k documents
- **Latence** : < 5s pour génération résumé
- **M-info** (Multimodal Information) pour contenus image+texte


## 🔒 Exigences sécurité (CRITIQUE)

### Authentification & Autorisation
- Firebase Auth JWT obligatoire
- Règles Firestore : utilisateur accède uniquement ses données
- Validation token côté backend FastAPI

### RGPD
- Consentement explicite collecte données
- Droit à l'effacement (suppression complète sur demande)
- Portabilité données (export JSON)
- Chiffrement transit (HTTPS/TLS) + repos (Firebase/S3)

### Gestion secrets
- Variables environnement (.env)
- AWS Secrets Manager / HashiCorp Vault pour clés API
- JAMAIS de clés en dur dans le code

### Monitoring
- Logging structuré JSON (INFO/WARNING/ERROR)
- Métriques : latence, throughput, taux erreurs
- Alertes sur erreurs critiques
- Tracing distribué (Jaeger/AWS X-Ray)