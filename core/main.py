"""
新闻推荐系统主程序
职责：程序入口、流程控制、结果展示
"""

import sys
from loguru import logger
from config import Config
from save_news_to_qdrant import NewsDataProcessor
from utils import NewsRecommender

# 配置日志系统
logger.remove()
logger.add(sys.stderr, level="INFO")


class NewsRecommendationApp:
   
    
    def __init__(self):
        self.config = Config()
        self.processor = NewsDataProcessor(self.config)
        self.recommender = NewsRecommender(self.config)
        
    def setup_data(self, force_rebuild: bool = False):
        """设置数据 - 检查向量数据库，如果需要则重建"""
        logger.info("=== 数据设置阶段 ===")
        
        # 检查向量数据库是否已存在数据
        if not force_rebuild and self.recommender.qdrant.collection_exists("news_vectors"):
            logger.info("向量数据库已存在，跳过数据入库")
            return True
            
        # 执行数据预处理和入库
        logger.info("开始数据预处理和向量入库...")
        success = self.processor.process_and_save(
            file_path='data/MIND/MINDsmall_train/news.tsv',
            collection_name="news_vectors",
            batch_size=500
        )
        
        if success:
            logger.success("✅ 数据入库完成")
            return True
        else:
            logger.error("❌ 数据入库失败")
            return False
    
    def run_recommendation_demo(self, num_users: int = 3):
        """运行推荐演示"""
        logger.info("=== 推荐演示阶段 ===")
        
        try:
            # 加载数据
            df_news = self.recommender.load_news_data()
            df_behaviors = self.recommender.load_behaviors_data()
            
            # 随机选择几个用户进行推荐演示
            sample_users = df_behaviors['user_id'].head(num_users).tolist()
            
            for i, user_id in enumerate(sample_users, 1):
                print(f"\n{'='*60}")
                print(f"第 {i} 个用户推荐演示 - 用户ID: {user_id}")
                print(f"{'='*60}")
                
                # 获取推荐结果
                recommendations = self.recommender.recommend(
                    df_news=df_news,
                    df_behaviors=df_behaviors,
                    user_id=user_id,
                    top_n=5
                )
                
                if not recommendations:
                    print(f"❌ 用户 {user_id} 无推荐结果")
                    continue
                
                # 显示用户点击历史
                user_history = self.recommender.get_user_history(df_behaviors, user_id)
                if not user_history.empty:
                    click_history = user_history['click_history'].iloc[0].split()[:5]
                    print(f"\n用户历史点击（最近5条）:")
                    for j, news_id in enumerate(click_history, 1):
                        news = df_news[df_news['news_id'] == news_id]
                        if not news.empty:
                            news_info = news.iloc[0]
                            print(f"  {j}. [{news_info['category']}] {news_info['title'][:50]}...")
                
                # 显示推荐结果
                print(f"\n🎯 为用户 {user_id} 的推荐结果:")
                for j, rec in enumerate(recommendations, 1):
                    title = rec['title'][:60] + '...' if len(rec['title']) > 60 else rec['title']
                    print(f"  {j}. [{rec['category']}/{rec['sub_category']}] {title}")
                
                print(f"\n推荐完成！共推荐 {len(recommendations)} 条新闻")
                
        except Exception as e:
            logger.error(f"推荐演示失败: {str(e)}")
    
    def interactive_mode(self):
        """交互模式 - 允许用户输入用户ID进行推荐"""
        logger.info("=== 交互模式 ===")
        
        try:
            # 加载数据
            df_news = self.recommender.load_news_data()
            df_behaviors = self.recommender.load_behaviors_data()
            
            print("\n🤖 进入交互推荐模式")
            print("输入用户ID获取推荐，输入 'quit' 退出")
            print(f"可选用户ID样例: {df_behaviors['user_id'].head(5).tolist()}")
            
            while True:
                user_input = input("\n请输入用户ID: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 退出交互模式")
                    break
                
                if not user_input:
                    print("请输入有效的用户ID")
                    continue
                
                # 检查用户是否存在
                if user_input not in df_behaviors['user_id'].values:
                    print(f"❌ 用户 {user_input} 不存在")
                    continue
                
                print(f"\n🔍 正在为用户 {user_input} 生成推荐...")
                
                recommendations = self.recommender.recommend(
                    df_news=df_news,
                    df_behaviors=df_behaviors,
                    user_id=user_input,
                    top_n=8
                )
                
                if not recommendations:
                    print(f"❌ 用户 {user_input} 无推荐结果")
                    continue
                
                print(f"\n🎯 推荐结果:")
                for i, rec in enumerate(recommendations, 1):
                    title = rec['title'][:50] + '...' if len(rec['title']) > 50 else rec['title']
                    print(f"  {i}. [{rec['category']}] {title}")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出交互模式")
        except Exception as e:
            logger.error(f"交互模式失败: {str(e)}")
    
    def run(self, mode: str = "demo", force_rebuild: bool = False):
        """主运行函数"""
        print("🚀 新闻推荐系统启动")
        print("="*50)
        
        # 1. 数据设置
        if not self.setup_data(force_rebuild):
            print("❌ 数据设置失败，程序退出")
            return
        
        # 2. 根据模式运行不同功能
        if mode == "demo":
            self.run_recommendation_demo(num_users=3)
        elif mode == "interactive":
            self.interactive_mode()
        elif mode == "setup_only":
            print("✅ 仅完成数据设置")
        else:
            print(f"❌ 未知模式: {mode}")
        
        print("\n🎉 程序运行完毕")

#==========================================
# Streamlit 应用部分
    """新闻推荐系统应用主类"""
    def get_all_user_ids(self):
        """返回所有用户ID列表"""
    # 假设推荐器有加载行为数据的方法
        try:
            df_behaviors = self.recommender.load_behaviors_data()
            return df_behaviors['user_id'][:50].unique().tolist()
        except Exception as e:
            from loguru import logger
            logger.error(f"获取用户ID失败: {e}")
            return []
    
    
    def recommend_for_user(self, user_id, top_n=5):
        # 加载新闻和行为数据（可优化为只加载一次）
        df_news = self.recommender.load_news_data()
        df_behaviors = self.recommender.load_behaviors_data()
        return self.recommender.recommend(df_news, df_behaviors, user_id, top_n)

    def get_user_profile(self, user_id):
        df_news = self.recommender.load_news_data()
        df_behaviors = self.recommender.load_behaviors_data()
        # 获取用户点击历史
        user_history = self.recommender.get_user_history(df_behaviors, user_id)
        if user_history.empty:
            return {}
        click_history_str = user_history['click_history'].iloc[0]
        click_history = click_history_str.split() if click_history_str else []
        return self.recommender.generate_user_profile(df_news, click_history)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="新闻推荐系统")
    parser.add_argument(
        "--mode", 
        choices=["demo", "interactive", "setup_only"], 
        default="demo",
        help="运行模式: demo(演示), interactive(交互), setup_only(仅数据设置)"
    )
    #重建太麻烦时间长就注释了
    # parser.add_argument(
    #     "--force-rebuild", 
    #     action="store_true",
    #     help="强制重建向量数据库"
    # )

    args = parser.parse_args()

    app = NewsRecommendationApp()
    # 如果 --force-rebuild 没有启用，这里会报 AttributeError
    # 建议加: force_rebuild = getattr(args, "force_rebuild", False)
    app.run(mode=args.mode, force_rebuild=getattr(args, "force_rebuild", False))

if __name__ == "__main__":
    main()
