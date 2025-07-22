from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Batch
from qdrant_client.http.exceptions import UnexpectedResponse
from typing import List, Dict, Any, Optional, Tuple, Union
from config import Config
from NewsGPT import DeepSeekGPT

class QdrantClientWrapper:
    """封装 Qdrant 客户端操作，提供更健壮的向量数据库访问"""
    def __init__(self, config: Config = None, client: QdrantClient = None):
        self.config = config or Config()
        self.client = client or QdrantClient(
            host=self.config.QDRANT_HOST,
            port=self.config.QDRANT_PORT
        )
        self.size = self.config.EMBEDDING_DIMS



    
    def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        collections = self.client.get_collections()
        return any(collection.name == collection_name 
                  for collection in collections.collections)
    
    def ensure_collection(self, collection_name: str) -> Tuple[bool, str]:
        """
        确保集合存在，如不存在则创建
        返回元组：(创建结果, 错误信息)
        """
        try:
            if not self.collection_exists(collection_name):
                logger.info(f"正在创建集合: {collection_name}")
                self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.size,
                        distance=Distance.COSINE
                    )
                )
                logger.success(f"集合创建成功: {collection_name}")
                return True, ""
            return True, ""
        except Exception as e:
            logger.error(f"集合创建失败: {collection_name} - 错误: {str(e)}")
            return False, str(e)
    
    def get_points_count(self, collection_name: str) -> int:
        """获取集合中的点数"""
        try:
            collection_info = self.client.get_collection(collection_name)
            return collection_info.points_count
        except (UnexpectedResponse, ValueError) as e:
            logger.warning(f"集合不存在: {collection_name}")
            success, _ = self.ensure_collection(collection_name)
            return 0 if success else -1
        except Exception as e:
            logger.error(f"获取集合信息错误: {collection_name} - 错误: {str(e)}")
            return -1

    def list_all_collection_names(self) -> List[str]:
        """获取所有集合名称"""
        collections = self.client.get_collections()
        return [collection.name for collection in collections.collections]

    def get_collection(self, collection_name: str) -> Any:
        """获取集合信息"""
        return self.client.get_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str) -> bool:
        """创建新集合"""
        success, error = self.ensure_collection(collection_name)
        if not success:
            raise RuntimeError(f"集合创建失败: {error}")
        return success

    def add_points(self, 
                  collection_name: str, 
                  ids: List[Union[int, str]], 
                  payloads: List[Dict[str, Any]], 
                  vectors: List[List[float]]) -> bool:
        """
        添加数据点到集合
        参数:
        - ids: 点的唯一标识列表
        - payloads: 元数据字典列表
        - vectors: 嵌入向量列表（必须外部生成）
        返回: 操作是否成功
        """
        if len(ids) != len(payloads):
            raise ValueError("ids和payloads长度必须相同")
        if len(ids) != len(vectors):
            raise ValueError("ids和vectors长度必须相同")
        success, error = self.ensure_collection(collection_name)
        if not success:
            return False
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=Batch(
                    ids=ids,
                    payloads=payloads,
                    vectors=vectors
                )
            )
            logger.success(f"成功添加 {len(ids)} 个点到集合: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"添加点到集合失败: {collection_name} - 错误: {str(e)}")
            return False

    def search(self, 
               collection_name: str, 
               query_vector: List[float], 
               limit: int = 3) -> List[Dict[str, Any]]:
        """向量搜索（外部传入向量）"""
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        return [self._format_search_result(r) for r in results]

    def search_with_filter(self, 
                           collection_name: str, 
                           query_vector: List[float], 
                           query_filter: Any, 
                           limit: int = 3) -> List[Dict[str, Any]]:
        """带过滤条件的向量搜索（外部传入向量）"""
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )
        return [self._format_search_result(r) for r in results]
    
    def _format_search_result(self, result) -> Dict[str, Any]:
        """格式化搜索结果为字典"""
        return {
            'id': result.id,
            'score': result.score,
            'payload': result.payload
        }


if __name__ == "__main__":
    # 测试集合操作
    qdrant = QdrantClientWrapper()
    
    # 测试集合操作
    collection_name = "test_collection"
    count = qdrant.get_points_count(collection_name)
    print(f"集合点数: {count}")
    
    # 测试添加和搜索
    if count <= 0:
        sample_data = [
            (1, {"category": "科技"}, "人工智能的发展趋势"),
            (2, {"category": "教育"}, "深度学习在教育中的应用"),
            (3, {"category": "科技"}, "大语言模型的技术原理")
        ]
        
        from NewsGPT import DeepSeekGPT
        gpt = DeepSeekGPT()
        ids, payloads, texts = zip(*sample_data)
        vectors = gpt.get_embeddings(list(texts))
        success = qdrant.add_points(collection_name, list(ids), list(payloads), vectors)
        
        if success:
            count = qdrant.get_points_count(collection_name)
            print(f"添加后集合点数: {count}")
    
    # 执行搜索
    if qdrant.get_points_count(collection_name) > 0:
        print("\n基本搜索:")
        query_vector = gpt.get_embeddings(["AI技术"])[0]
        results = qdrant.search(collection_name, query_vector, limit=2)
        for result in results:
            print(f"ID: {result['id']}, 分数: {result['score']:.4f}, 内容: {result['payload']}")

        print("\n过滤搜索:")
        from qdrant_client.http import models
        category_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="category",
                    match=models.MatchValue(value="科技")
                )
            ]
        )
        query_vector = gpt.get_embeddings(["技术"])[0]
        results = qdrant.search_with_filter(collection_name, query_vector, category_filter, limit=2)
        for result in results:
            print(f"ID: {result['id']}, 分数: {result['score']:.4f}, 内容: {result['payload']}")
