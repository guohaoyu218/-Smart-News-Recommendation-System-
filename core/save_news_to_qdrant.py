"""
数据预处理和向量数据库入库模块
职责：专门负责新闻数据的预处理、向量生成和批量入库到Qdrant
"""

import pandas as pd
from ast import literal_eval
from loguru import logger
from typing import Tuple, List, Dict, Any
from config import Config
from db_qdrant import QdrantClientWrapper
from NewsGPT import DeepSeekGPT
import uuid


class NewsDataProcessor:
    """新闻数据处理器 - 专门负责数据入库"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.gpt = DeepSeekGPT(self.config)
        self.qdrant = QdrantClientWrapper(self.config)
    
    def load_news_data(self, file_path: str = 'MIND/MINDsmall_train/news.tsv') -> pd.DataFrame:
        """加载新闻数据"""
        df = pd.read_csv(
            file_path,
            names=[
                "news_id", "category", "sub_category", "title", "abstract",
                "url", "title_entities", "abstract_entities"
            ],
            sep='\t',
            header=None
        )
        logger.info(f"新闻数据加载完成 | 记录数: {len(df)}")
        return df
    
    def preprocess_data(self, df_news: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        数据预处理
        - 转换实体列表
        - 填充缺失值  
        - 创建新闻信息字符串
        """
        df_news = df_news.copy()
        
        # 安全转换字符串表示的列表
        for col in ['title_entities', 'abstract_entities']:
            if col in df_news.columns:
                df_news[col] = df_news[col].apply(
                    lambda x: literal_eval(x) if pd.notna(x) and x.strip() else []
                )
        
        # 填充缺失值并创建新闻信息
        df_news = df_news.fillna('')
        info_parts = ["category", "sub_category", "title", "abstract"]
        
        # 仅包含实际存在的列
        valid_parts = [col for col in info_parts if col in df_news.columns]
        df_news['news_info'] = df_news.apply(
            lambda row: ' | '.join(f"{col}:{row[col]}" for col in valid_parts),
            axis=1
        )
        
        logger.info(f"数据预处理完成 | 记录数: {len(df_news)}")
        return df_news, df_news['news_info'].tolist()
    
    def compute_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 500
    ) -> List[List[float]]:
        """批量计算嵌入向量"""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.gpt.get_embeddings(batch)
            all_embeddings.extend(embeddings)#extend 添加
            logger.info(f"嵌入计算进度: {min(i + batch_size, len(texts))}/{len(texts)}")
        
        logger.success(f"嵌入计算完成 | 总数: {len(all_embeddings)}")
        return all_embeddings
    
    def save_to_qdrant(
        self,
        df_news: pd.DataFrame,
        embeddings: List[List[float]],
        collection_name: str = "news_vectors",
        batch_size: int = 1000
    ) -> bool:
        """将数据批量保存到Qdrant"""
        df_news = df_news.copy()
        df_news['point_id'] = [str(uuid.uuid5(uuid.NAMESPACE_DNS, str(nid))) for nid in df_news['news_id']]
        ids = df_news['point_id'].tolist()
        
        # 确保集合存在
        success = self.qdrant.create_collection(collection_name)
        if not success:
            return False
        
        total_points = 0
        payloads = df_news.to_dict(orient='records')#orient='records'参数会将每一行转换为一个字典
        
        for i in range(0, len(embeddings), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_payloads = payloads[i:i + batch_size]
            
            success = self.qdrant.add_points(
                collection_name=collection_name,
                ids=batch_ids,
                vectors=batch_embeddings,
                payloads=batch_payloads
            )
            
            if success:
                total_points += len(batch_ids)
                logger.info(f"批次 {i//batch_size + 1} 插入成功 | 点数: {len(batch_ids)}")
            else:
                logger.error(f"批次 {i//batch_size + 1} 插入失败")
        
        logger.success(f"数据插入完成 | 总数: {total_points} | 集合: {collection_name}")
        return True
    
    def process_and_save(
        self,
        file_path: str = 'MIND/MINDsmall_train/news.tsv',
        collection_name: str = "news_vectors",
        batch_size: int = 500
    ) -> bool:
        """完整的数据处理和入库流程"""
        try:
            # 1. 加载数据
            df_news = self.load_news_data(file_path)
            
            # 2. 预处理
            df_news, news_info_list = self.preprocess_data(df_news)
            
            # 3. 计算嵌入向量
            embeddings = self.compute_embeddings_batch(news_info_list, batch_size)
            
            # 4. 保存到Qdrant
            return self.save_to_qdrant(df_news, embeddings, collection_name, batch_size)
            
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}")
            return False


if __name__ == "__main__":
    # 执行数据入库
    processor = NewsDataProcessor()
    success = processor.process_and_save()
    
    if success:
        print("✅ 新闻数据入库完成")
    else:
        print("❌ 新闻数据入库失败")