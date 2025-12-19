import chromadb 
import pandas as pd

class ChromaPeek:
    def __init__(self, path):
        self.client = chromadb.PersistentClient(path)

    ## function that returs all collection's name
    def get_collections(self):
        collections = []

        for i in self.client.list_collections():
            collections.append(i.name)
        
        return collections
    
    ## function to return documents/ data inside the collection
    def get_collection_data(self, collection_name, dataframe=False):
        data = self.client.get_collection(name=collection_name).get()
        if dataframe:
            # Transform ChromaDB data structure into a proper DataFrame
            # ChromaDB returns: {'ids': [...], 'documents': [...], 'metadatas': [...], 'embeddings': [...]}
            rows = []
            ids = data.get('ids', [])
            documents = data.get('documents', [])
            metadatas_raw = data.get('metadatas')
            embeddings_raw = data.get('embeddings')
            
            # Handle metadatas: can be None, empty list, or list of dicts/None
            if metadatas_raw is None:
                metadatas = [None] * len(ids) if ids else []
            else:
                metadatas = metadatas_raw
            
            # Handle embeddings: can be None, empty list, or list of arrays
            if embeddings_raw is None:
                embeddings = [None] * len(ids) if ids else []
            else:
                embeddings = embeddings_raw
            
            # Ensure all lists have the same length
            max_len = max(len(ids), len(documents), len(metadatas) if metadatas else 0, len(embeddings) if embeddings else 0)
            
            # Handle empty collection
            if max_len == 0:
                return pd.DataFrame(columns=['id', 'document'])
            
            for i in range(max_len):
                row = {
                    'id': ids[i] if i < len(ids) else None,
                    'document': documents[i] if i < len(documents) else None,
                }
                
                # Add metadata fields if available
                if metadatas and i < len(metadatas) and metadatas[i] is not None:
                    if isinstance(metadatas[i], dict):
                        row.update(metadatas[i])
                    else:
                        row['metadata'] = metadatas[i]
                
                # Add embedding info (just length, not the full vector)
                if embeddings and i < len(embeddings) and embeddings[i] is not None:
                    row['embedding_length'] = len(embeddings[i])
                else:
                    row['embedding_length'] = None
                
                rows.append(row)
            
            return pd.DataFrame(rows)
        return data
    
    ## function to query the selected collection
    def query(self, query_str, collection_name, k=3, dataframe=False):
        collection = self.client.get_collection(collection_name)
        collection_data = collection.get()
        collection_size = len(collection_data.get('ids', [])) if collection_data else 0
        n_results = min(k, collection_size) if collection_size > 0 else k
        res = collection.query(
            query_texts=[query_str], n_results=n_results
        )
        
        if dataframe:
            # Transform query results into a proper DataFrame
            rows = []
            ids = res.get('ids', [[]])[0] if res.get('ids') and res.get('ids')[0] else []
            documents = res.get('documents', [[]])[0] if res.get('documents') and res.get('documents')[0] else []
            metadatas_raw = res.get('metadatas', [[]])[0] if res.get('metadatas') and res.get('metadatas')[0] else []
            distances = res.get('distances', [[]])[0] if res.get('distances') and res.get('distances')[0] else []
            
            # Handle empty results
            if not ids and not documents:
                return pd.DataFrame(columns=['id', 'document', 'distance'])
            
            max_len = max(len(ids), len(documents), len(metadatas_raw) if metadatas_raw else 0, len(distances) if distances else 0)
            
            for i in range(max_len):
                row = {
                    'id': ids[i] if i < len(ids) else None,
                    'document': documents[i] if i < len(documents) else None,
                    'distance': distances[i] if i < len(distances) else None,
                }
                
                # Add metadata fields if available
                if metadatas_raw and i < len(metadatas_raw) and metadatas_raw[i] is not None:
                    if isinstance(metadatas_raw[i], dict):
                        row.update(metadatas_raw[i])
                    else:
                        row['metadata'] = metadatas_raw[i]
                
                rows.append(row)
            
            return pd.DataFrame(rows)
        
        return res