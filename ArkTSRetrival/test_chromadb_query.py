def search_with_chunks(collection, query, top_k=5):
    # 第一步：检索相关块
    results = collection.query(
        query_texts=[query],
        n_results=top_k*3  # 扩大召回量
    )
    
    # 第二步：结果聚合
    grouped = {}
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        original_id = meta['original_id']
        if original_id not in grouped:
            grouped[original_id] = {
                'score': meta.get('score', 0),
                'chunks': [doc],
                'metadata': meta
            }
        else:
            grouped[original_id]['score'] += meta.get('score', 0)
            grouped[original_id]['chunks'].append(doc)
    
    # 第三步：按聚合分数排序
    sorted_results = sorted(grouped.values(), key=lambda x: x['score'], reverse=True)
    return sorted_results[:top_k]