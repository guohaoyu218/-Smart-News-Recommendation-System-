

"""
新闻内容分析与可视化工具
功能：词云生成、情感分析、热点话题挖掘
"""
import streamlit as st
import pandas as pd
import numpy as np
import jieba
import jieba.analyse
from collections import Counter
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from main import NewsRecommendationApp
import matplotlib.pyplot as plt
import re
from datetime import datetime

def main():
    # 移除page_config，避免与主应用冲突
    
    # CSS样式
    st.markdown("""
    <style>
    .analysis-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .analysis-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 4px solid #667eea;
    }
    .keyword-tag {
        display: inline-block;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        font-weight: 500;
    }
    .sentiment-positive {
        color: #2ECC71;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #E74C3C;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #F39C12;
        font-weight: bold;
    }
    .topic-item {
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 12px;
    }
    .stats-box {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.markdown("""
    <div class="analysis-header">
        <h1>📝 新闻内容深度分析工具</h1>
        <p>智能挖掘新闻内容特征，分析热点话题与用户偏好</p>
    </div>
    """, unsafe_allow_html=True)

    # 初始化应用
    app = NewsRecommendationApp()

    # 文本预处理函数
    def preprocess_text(text):
        if not text:
            return ""
        text = re.sub(r'[^\u4e00-\u9fa5]', '', str(text))
        words = jieba.cut(text)
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '们', '来', '还', '时候', '过', '什么', '为'}
        filtered_words = [word for word in words if len(word) > 1 and word not in stopwords]
        return filtered_words

    def analyze_sentiment(text):
        positive_words = ['好', '棒', '赞', '优秀', '精彩', '成功', '获胜', '提升', '增长', '突破']
        negative_words = ['坏', '差', '糟糕', '失败', '下降', '损失', '事故', '危险', '问题', '困难']
        text = str(text).lower()
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        if pos_count > neg_count:
            return "积极", pos_count
        elif neg_count > pos_count:
            return "消极", neg_count
        else:
            return "中性", 0

    @st.cache_data
    def load_and_analyze_news():
        try:
            df_news = app.recommender.load_news_data()
            sample_size = min(1000, len(df_news))
            df_sample = df_news.sample(n=sample_size, random_state=42)
            analysis_results = {
                'total_news': len(df_news),
                'sample_size': sample_size,
                'categories': df_sample['category'].value_counts().to_dict(),
                'subcategories': df_sample['sub_category'].value_counts().head(10).to_dict(),
                'keywords': [],
                'sentiments': {'积极': 0, '消极': 0, '中性': 0},
                'hot_topics': []
            }
            all_words = []
            sentiment_results = []
            for _, row in df_sample.iterrows():
                title_words = preprocess_text(row['title'])
                abstract_words = preprocess_text(row['abstract'])
                all_words.extend(title_words + abstract_words)
                sentiment, score = analyze_sentiment(row['title'] + ' ' + str(row['abstract']))
                sentiment_results.append(sentiment)
            word_freq = Counter(all_words)
            analysis_results['keywords'] = word_freq.most_common(30)
            sentiment_count = Counter(sentiment_results)
            analysis_results['sentiments'] = dict(sentiment_count)
            hot_topics = []
            for word, freq in word_freq.most_common(10):
                if freq > 5:
                    hot_topics.append(f"{word} ({freq}次)")
            analysis_results['hot_topics'] = hot_topics
            return analysis_results, df_sample
        except Exception as e:
            st.error(f"数据加载失败: {str(e)}")
            return None, None

    with st.spinner("🔍 正在分析新闻内容，请稍候..."):
        analysis_results, df_sample = load_and_analyze_news()

    if analysis_results:
        st.markdown("## 📊 数据概览")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stats-box">
                <h3>{analysis_results['total_news']:,}</h3>
                <p>总新闻数</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stats-box">
                <h3>{len(analysis_results['categories'])}</h3>
                <p>新闻类别</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stats-box">
                <h3>{len(analysis_results['keywords'])}</h3>
                <p>热门关键词</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stats-box">
                <h3>{analysis_results['sample_size']:,}</h3>
                <p>分析样本</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("## 📈 类别分布分析")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("### 🏷️ 主要类别分布")
            categories_df = pd.DataFrame(
                list(analysis_results['categories'].items()),
                columns=['Category', 'Count']
            ).head(10)
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(categories_df['Category'], categories_df['Count'], 
                        color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', 
                            '#00f2fe', '#a8edea', '#fed6e3', '#ffecd2', '#fcb69f'])
            ax.set_title('新闻类别分布', fontsize=16, fontweight='bold')
            ax.set_xlabel('类别')
            ax.set_ylabel('数量')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("### 📊 子类别Top10")
            subcategories = analysis_results['subcategories']
            for subcat, count in list(subcategories.items())[:8]:
                percentage = (count / analysis_results['sample_size']) * 100
                st.write(f"**{subcat}**: {count} ({percentage:.1f}%)")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("## 🔍 关键词分析")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("### 🏆 热门关键词Top20")
            keywords = analysis_results['keywords'][:20]
            keyword_html = ""
            for word, freq in keywords:
                keyword_html += f'<span class="keyword-tag">{word} ({freq})</span>'
            st.markdown(keyword_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 热点话题")
            hot_topics = analysis_results['hot_topics'][:8]
            for i, topic in enumerate(hot_topics, 1):
                st.markdown(f"""
                <div class="topic-item">
                    <strong>#{i}</strong> {topic}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("## 💭 情感分析")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("### 😊 情感倾向分布")
            sentiments = analysis_results['sentiments']
            total_sentiment = sum(sentiments.values())
            for sentiment, count in sentiments.items():
                percentage = (count / total_sentiment) * 100 if total_sentiment > 0 else 0
                if sentiment == '积极':
                    st.markdown(f'<p class="sentiment-positive">😊 积极: {count} ({percentage:.1f}%)</p>', unsafe_allow_html=True)
                elif sentiment == '消极':
                    st.markdown(f'<p class="sentiment-negative">😔 消极: {count} ({percentage:.1f}%)</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="sentiment-neutral">😐 中性: {count} ({percentage:.1f}%)</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("### 📊 情感趋势图")
            if sentiments:
                labels = list(sentiments.keys())
                sizes = list(sentiments.values())
                colors = ['#2ECC71', '#E74C3C', '#F39C12']
                fig, ax = plt.subplots(figsize=(8, 6))
                wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                ax.set_title('新闻情感分布', fontsize=14, fontweight='bold')
                plt.rcParams['font.sans-serif'] = ['SimHei']
                st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("## 📋 详细数据")
        with st.expander("查看原始数据样例"):
            if df_sample is not None:
                display_cols = ['news_id', 'category', 'sub_category', 'title', 'abstract']
                available_cols = [col for col in display_cols if col in df_sample.columns]
                st.dataframe(
                    df_sample[available_cols].head(20),
                    use_container_width=True
                )
        st.markdown("## 📄 分析报告")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 生成分析报告", type="primary"):
                report = f"""
# 新闻内容分析报告

## 数据概览
- 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 总新闻数：{analysis_results['total_news']:,}
- 分析样本：{analysis_results['sample_size']:,}
- 新闻类别：{len(analysis_results['categories'])}

## 热门关键词
{', '.join([word for word, _ in analysis_results['keywords'][:10]])}

## 情感分析结果
- 积极：{analysis_results['sentiments'].get('积极', 0)}条
- 消极：{analysis_results['sentiments'].get('消极', 0)}条  
- 中性：{analysis_results['sentiments'].get('中性', 0)}条

## 热点话题
{chr(10).join([f"- {topic}" for topic in analysis_results['hot_topics'][:5]])}
"""
                st.download_button(
                    label="📥 下载报告",
                    data=report,
                    file_name=f"news_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        with col2:
            if st.button("🔄 重新分析", type="secondary"):
                st.cache_data.clear()
                st.rerun()
    else:
        st.error("❌ 数据分析失败，请检查系统状态。")
    st.markdown("""
    <div style="text-align: center; padding: 40px 0; color: #7F8C8D;">
        <hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #BDC3C7, transparent);">
        <p>📝 新闻内容分析工具 | 基于中文自然语言处理技术</p>
        <p style="font-size: 12px;">使用结巴分词进行文本处理 | © 2024 AI News Platform</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
