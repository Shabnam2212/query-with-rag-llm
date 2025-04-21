This code converts scientific fulltext XML files into Markdown, chunks them smartly, and builds a retrieval-augmented generation (RAG) pipeline using LangChain, HuggingFaceEmbeddings, and ChromaDB.

 Features
 Parses NXML files to extract structured scientific content

 Saves cleaned Markdown outputs with metadata (title, authors, DOI)

 Chunks intelligently (hybrid strategy for short + long documents)

 Builds a vector store using all-mpnet-base-v2 embeddings

 Prepares a ChromaDB collection for downstream QA/RAG tasks
