"""
新闻推荐系统核心模块
职责：用户画像分析、推荐算法、向量搜索等核心推荐逻辑
"""

import pandas as pd
from loguru import logger
from typing import List, Dict, Any
from collections import Counter
from config import Config
from NewsGPT import DeepSeekGPT
from db_qdrant import QdrantClientWrapper
import re


class NewsRecommender:
    """新闻推荐系统核心类"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.gpt = DeepSeekGPT(self.config)
        self.qdrant = QdrantClientWrapper(self.config)
        self.news_collection = "news_vectors"
    
    def load_news_data(self, file_path: str = 'MIND/MINDsmall_train/news.tsv') -> pd.DataFrame:
        """加载新闻数据（只加载，不处理）"""
        df = pd.read_csv(
            file_path,
            names=[
                "news_id", "category", "sub_category", "title", "abstract",
                "url", "title_entities", "abstract_entities"
            ],
            sep='\t',
            header=None
        )
       # logger.info(f"新闻数据加载完成 | 记录数: {len(df)}")
        return df
    
    def load_behaviors_data(self, file_path: str = 'MIND/MINDsmall_train/behaviors.tsv') -> pd.DataFrame:
        """加载用户行为数据"""
        df = pd.read_csv(
            file_path,
            names=[
                "impression_id", "user_id", "time",
                "click_history", "impression_lpg"
            ],
            sep='\t',
            header=None
        )
        #logger.info(f"用户行为数据加载完成 | 记录数: {len(df)}")
        return df
    
    def get_user_history(self, df_behaviors: pd.DataFrame, user_id: str, sample_size: int = 10) -> pd.DataFrame:
        """获取特定用户的行为历史"""
        user_behaviors = df_behaviors[df_behaviors['user_id'] == user_id]
        return user_behaviors.head(sample_size)
    
    def analyze_user_categories(self, df_news: pd.DataFrame, click_history: List[str]) -> Dict[str, Any]:
        """分析用户偏好类别"""
        category_counter = Counter()
        
        for news_id in click_history:
            news = df_news[df_news['news_id'] == news_id]
            if not news.empty:
                category = news['category'].values[0]
                sub_category = news['sub_category'].values[0]
                category_counter.update([(category, sub_category)])
        
        return {
            "favorite_categories": dict(category_counter.most_common(5)),
            "top_category": category_counter.most_common(1)[0] if category_counter else None
        }
    
    def generate_user_profile(self, df_news: pd.DataFrame, click_history: List[str]) -> Dict[str, Any]:
        """生成完整用户画像"""
        # 生成历史记录摘要
        historical_records = []
        #枚举功能：enumerate(..., start=1) 将这 10 条新闻 ID 转换为带序号的元组 (序号, 新闻ID)，序号从 1 开始。
        for idx, news_id in enumerate(click_history[:10], start=1):
            news = df_news[df_news['news_id'] == news_id]
            if not news.empty:
                row = news.iloc[0]#iloc[0] 用于获取 DataFrame 的第一行数据
                record = f"{idx}. category:{row['category']} | sub_category:{row['sub_category']} | title:{row['title']}"
                historical_records.append(record)
        
        historical_records_str = "\n".join(historical_records)
        
        # GPT生成用户画像
        prompt = f"""基于以下用户浏览历史，描述用户兴趣画像:

{historical_records_str}

请按以下格式描述:
[topics]
- 主题1
- 主题2

[region]  
- 地区1
"""
        
        logger.debug(f"生成用户画像提示: {prompt[:200]}...")
        user_profile_text = self.gpt.get_completion(prompt, temperature=0.5)
        #logger.info(f"GPT生成用户画像: {user_profile_text}")
        
        # 分析类别偏好
        category_analysis = self.analyze_user_categories(df_news, click_history)
        
        return {
            "topics": self._extract_profile_section(user_profile_text, "topics"),
            "regions": self._extract_profile_section(user_profile_text, "region"),
            "favorite_categories": category_analysis["favorite_categories"],
            "click_history": click_history[:10]  # 保留最近10个点击
        }
    
    def _extract_profile_section(self, profile: str, section: str) -> List[str]:
        """从GPT生成的用户画像文本中提取特定部分"""
        try:
            start_idx = profile.lower().index(f"[{section}]")
            end_idx = profile.find("[", start_idx + 1) if section != "region" else len(profile)
            section_text = profile[start_idx:end_idx].strip()
            
            return [
                line.strip("- ").strip()
                for line in section_text.split("\n")[1:]
                if line.strip()
            ]
        except (ValueError, IndexError):
            logger.warning(f"无法解析{section}部分: {profile[:100]}...")
            return []
    
    def vector_search_candidates(self, query_text: str, limit: int = 30) -> List[str]:
        """使用向量搜索获取候选新闻"""
        try:
            # 将查询文本转为向量
            query_vector = self.gpt.get_embeddings([query_text])[0]
            
            # 向量搜索
            results = self.qdrant.search(
                collection_name=self.news_collection,
                query_vector=query_vector,
                limit=limit
            )
            
            # 从payload中提取原始news_id，而不是使用Qdrant的点ID
            news_ids = []
            for result in results:
                if 'payload' in result and 'news_id' in result['payload']:
                    news_ids.append(result['payload']['news_id'])
                else:
                    # 如果payload中没有news_id，记录警告并跳过
                    logger.warning(f"搜索结果缺少news_id: {result}")
            
            logger.info(f"向量搜索成功，返回{len(news_ids)}个候选新闻ID")
            return news_ids
            
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return []
    
    def rank_news_by_profile(
        self,
        df_news: pd.DataFrame,
        user_profile: Dict[str, Any],
        candidate_ids: List[str],
        top_n: int = 5
    ) -> List[str]:
        """基于用户画像对候选新闻进行排序"""
        #logger.info(f"排序输入: candidate_ids={len(candidate_ids)}, top_n={top_n}")
        
        candidate_news = df_news[df_news['news_id'].isin(candidate_ids)]
        #df_news['news_id'].isin(candidate_ids) 返回的是一个布尔序列（Series
        if candidate_news.empty:
            logger.warning("候选新闻为空，返回空列表")
            return []
        
        #logger.info(f"匹配到的候选新闻数量: {len(candidate_news)}")
        
        # 构建候选新闻列表
        candidate_list = "\n".join([
            f"{idx}. category:{row['category']} | sub_category:{row['sub_category']} | title:{row['title']}"
            for idx, (_, row) in enumerate(candidate_news.iterrows(), 1)
        ])
        #遍历 DataFrame，每次返回 (索引, 行数据)
        #enumerate(..., 1)：给每条新闻加上从 1 开始的序号
        #row['category']、row['sub_category']、row['title']：分别取出每条新闻的类别、子类别和标题。
        
        #logger.info(f"候选新闻列表前200字符: {candidate_list[:200]}...")
        
        # GPT排序提示
        #.keys() 取出所有类别名（比如 "科技", "教育", "娱乐"）   
        prompt = f"""
请基于用户画像对候选新闻进行排序，返回最符合用户兴趣的{top_n}条新闻。

用户画像:
兴趣主题: {', '.join(user_profile['topics'])}
关注地区: {', '.join(user_profile['regions'])}
偏好类别: {list(user_profile['favorite_categories'].keys())[:3]}

候选新闻列表:
{candidate_list}

请只输出新闻序号，用逗号分隔（如: 1,3,5,2,4）
"""
    

        logger.debug(f"新闻排序提示: {prompt[:300]}...")
        response = self.gpt.get_completion(prompt, temperature=0.3)
      #  logger.info(f"GPT排序结果: {response}")
        
        # 解析排序结果
        try:
            # 替换原来的解析方式
            recommended_indices = [int(idx) for idx in re.findall(r'\d+', response) if 1 <= int(idx) <= len(candidate_news)]
            recommended_indices = recommended_indices[:top_n]
            result_ids = []
            for idx in recommended_indices:
                news_id = candidate_news.iloc[idx-1]['news_id']
                result_ids.append(news_id)
                logger.debug(f"添加推荐新闻: {idx} -> {news_id}")
            # 如果推荐数量不足，补齐兜底新闻
            if len(result_ids) < top_n:
                fallback_ids = candidate_news.head(top_n - len(result_ids))['news_id'].tolist()
                result_ids.extend(fallback_ids)
            return result_ids
        except (ValueError, IndexError) as e:
            logger.error(f"排序结果解析失败: {str(e)}")
            fallback_ids = candidate_news.head(top_n)['news_id'].tolist()
            return fallback_ids
    
    def recommend(
        self,
        df_news: pd.DataFrame,
        df_behaviors: pd.DataFrame,
        user_id: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """完整推荐流程"""
        # 1. 获取用户历史
        user_history = self.get_user_history(df_behaviors, user_id)
        if user_history.empty:
            logger.warning(f"用户 {user_id} 没有历史行为")
            return []
        
        # 2. 解析点击历史
        click_history_str = user_history['click_history'].iloc[0]
        click_history = click_history_str.split() if click_history_str else []
        
        if not click_history:
            logger.warning(f"用户 {user_id} 没有点击历史")
            return []
        
        # 3. 生成用户画像
        user_profile = self.generate_user_profile(df_news, click_history)
        
        # 4. 向量搜索候选新闻（使用最近点击的新闻标题作为查询）
        latest_news = df_news[df_news['news_id'] == click_history[-1]]
        query_text = latest_news.iloc[0]['title'] if not latest_news.empty else "新闻"
        
        candidate_ids = self.vector_search_candidates(query_text, limit=top_n * 3)
        
        # 5. 如果向量搜索失败，使用随机候选
        if not candidate_ids:
            candidate_ids = df_news.sample(min(50, len(df_news)))['news_id'].tolist()
            logger.warning("向量搜索失败，使用随机候选新闻")
        
        # 添加调试日志
        #logger.info(f"候选新闻数量: {len(candidate_ids)}")
        #logger.info(f"候选新闻ID前5个: {candidate_ids[:5]}")
        
        # 6. 基于用户画像排序
        recommended_ids = self.rank_news_by_profile(df_news, user_profile, candidate_ids, top_n)
        
        # 添加调试日志
        #logger.info(f"推荐新闻ID数量: {len(recommended_ids)}")
        #logger.info(f"推荐新闻ID: {recommended_ids}")
       
        # 7. 返回推荐结果
        result = []
        for news_id in recommended_ids:
            news = df_news[df_news['news_id'] == news_id]
            if not news.empty:
                news_info = news.iloc[0]
                result.append({
                    'news_id': news_id,
                    'title': news_info['title'],
                    'category': news_info['category'],
                    'sub_category': news_info['sub_category'],
                    'abstract': news_info['abstract']
                })
        
        logger.info(f"最终推荐结果数量: {len(result)}")
        return result


if __name__ == "__main__":
    # 简单测试
    recommender = NewsRecommender()
    
    # 加载数据
    df_news = recommender.load_news_data()
    df_behaviors = recommender.load_behaviors_data()
    
    # 随机选择一个用户测试
    test_user = df_behaviors['user_id'].iloc[0]
    recommendations = recommender.recommend(df_news, df_behaviors, test_user, top_n=5)
    
    print(f"\n为用户 {test_user} 的推荐结果:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['category']}/{rec['sub_category']}] {rec['title']}")
