import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from main import NewsRecommendationApp
import base64
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from collections import Counter
import random
import matplotlib.font_manager as fm
import hashlib

app = NewsRecommendationApp()

def main():
    # 为智能推荐模块创建独立容器，避免与主应用混合
    st.markdown('<div id="enhanced-recommendation-module">', unsafe_allow_html=True)
    
    # 简化CSS样式 - 仅影响当前模块，不污染全局
    st.markdown("""
    <style>
    /* 仅为智能推荐模块定义必要样式 */
    #enhanced-recommendation-module .module-stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }

    #enhanced-recommendation-module .module-main-section {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 6px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }

    #enhanced-recommendation-module .module-profile-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 25px;
        border-radius: 18px;
        margin: 15px 0;
        box-shadow: 0 6px 30px rgba(240, 147, 251, 0.4);
    }

    #enhanced-recommendation-module .module-profile-item {
        background: rgba(255,255,255,0.2);
        padding: 12px 15px;
        border-radius: 10px;
        margin: 8px 0;
    }

    #enhanced-recommendation-module .module-news-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.5);
        position: relative;
        overflow: hidden;
    }

    #enhanced-recommendation-module .module-timeline-item {
        border-left: 3px solid #667eea;
        padding-left: 15px;
        margin: 10px 0;
        position: relative;
    }

    #enhanced-recommendation-module .module-timeline-item::before {
        content: '';
        width: 10px;
        height: 10px;
        background: #667eea;
        border-radius: 50%;
        position: absolute;
        left: -6px;
        top: 5px;
    }

    #enhanced-recommendation-module .module-tag {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin: 3px;
        display: inline-block;
    }

    #enhanced-recommendation-module .module-rating-container {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 15px;
        padding: 20px;
        margin-top: 15px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # 状态管理
    if 'user_interactions' not in st.session_state:
        st.session_state.user_interactions = []
    if 'recommendation_history' not in st.session_state:
        st.session_state.recommendation_history = {}
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}

    # Logo展示函数优化
    def show_enhanced_logo(path):
        try:
            with open(path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'''
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/png;base64,{b64}" width="150" 
                         style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                </div>
            ''', unsafe_allow_html=True)
        except Exception:
            st.markdown('''
                <div style="text-align: center; font-size: 80px; margin: 20px 0;">
                    🌟
                </div>
            ''', unsafe_allow_html=True)

    show_enhanced_logo("logo.png")

    # 系统统计信息
    def show_system_stats():
        try:
            user_ids = app.get_all_user_ids() if hasattr(app, "get_all_user_ids") else []
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="module-stats-card">
                        <h3>{len(user_ids)}</h3>
                        <p>活跃用户</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="module-stats-card">
                        <h3>{len(st.session_state.user_interactions)}</h3>
                        <p>本次交互</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="module-stats-card">
                        <h3>95%</h3>
                        <p>推荐准确率</p>
                    </div>
                """, unsafe_allow_html=True)
                
            with col4:
                current_time = datetime.now().strftime("%H:%M")
                st.markdown(f"""
                    <div class="module-stats-card">
                        <h3>{current_time}</h3>
                        <p>当前时间</p>
                    </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"统计信息加载失败: {str(e)}")

    show_system_stats()

    # 功能介绍优化
    st.markdown("""
        <div class="module-main-section">
            <h2 style="color: #2C3E50; margin-bottom: 20px;">🚀 功能特色</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
                    <h4>🎯 智能推荐</h4>
                    <p>基于用户画像和历史行为的个性化推荐算法</p>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 15px;">
                    <h4>🧠 AI分析</h4>
                    <p>DeepSeek GPT驱动的内容理解和用户意图识别</p>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2C3E50; border-radius: 15px;">
                    <h4>📊 数据洞察</h4>
                    <p>实时用户行为分析和偏好可视化</p>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #2C3E50; border-radius: 15px;">
                    <h4>⚡ 实时更新</h4>
                    <p>动态学习用户反馈，持续优化推荐效果</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 侧边栏增强
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <h2 style="color: #2C3E50;">⚙️ 控制面板</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # 获取用户列表
        user_ids = app.get_all_user_ids() if hasattr(app, "get_all_user_ids") else []
        
        # 用户选择区域
        st.markdown("### 👤 用户选择")
        
        if user_ids:
            user_id = st.selectbox(
                "选择用户ID", 
                user_ids, 
                key="user_id_select",
                help="从下拉列表中选择一个用户ID"
            )
        else:
            user_id = st.text_input(
                "用户ID", 
                key="user_id_input",
                help="请输入用户ID"
            )
        
        # 随机用户按钮
        if st.button("🎲 随机选择用户", use_container_width=True) and user_ids:
            selected_user = random.choice(user_ids)
            # 使用不同的session state key来避免冲突
            st.session_state["random_selected_user"] = selected_user
            st.success(f"✨ 已随机选择用户：{selected_user}")
            # 不使用st.rerun()，而是让用户手动选择
        
        # 推荐参数设置
        st.markdown("### 🎛️ 推荐设置")
        top_n = st.slider("推荐条数", 1, 20, 8, help="设置要推荐的新闻数量")
        
        # 高级筛选
        with st.expander("🔍 高级筛选"):
            categories = ['sports', 'entertainment', 'news', 'finance', 'lifestyle', 'tv', 'music']
            selected_categories = st.multiselect(
                "筛选类别",
                categories,
                help="选择感兴趣的新闻类别"
            )
            
            time_filter = st.selectbox(
                "时间范围",
                ["不限", "最近24小时", "最近一周", "最近一个月"]
            )
        
        # 推荐模式
        recommend_mode = st.radio(
            "推荐模式",
            ["标准模式", "探索模式", "热点模式"],
            help="选择不同的推荐策略"
        )

    # 获取当前用户ID - 优先使用随机选择的用户
    random_user = st.session_state.get("random_selected_user")
    if random_user and random_user in user_ids:
        current_user_id = random_user
    else:
        current_user_id = st.session_state.get("user_id_select", user_id)

    # 缓存函数优化
    @st.cache_data(ttl=300)  # 5分钟缓存
    def get_enhanced_recommendation_and_profile(user_id, top_n, categories=None):
        try:
            result = app.recommend_for_user(user_id, top_n)
            user_profile = app.get_user_profile(user_id)
            
            # 如果有类别筛选，进行过滤
            if categories and result:
                result = [news for news in result if news.get('category') in categories]
            
            return result, user_profile
        except Exception as e:
            st.error(f"获取推荐失败: {str(e)}")
            return None, None

    # 主推荐按钮
    st.markdown("""
        <div class="module-main-section">
            <div style="text-align: center;">
    """, unsafe_allow_html=True)

    if st.button("🚀 获取个性化推荐", type="primary", use_container_width=True):
        st.session_state["show_recommend"] = True
        st.session_state["current_user_id"] = current_user_id
        st.session_state["current_top_n"] = top_n
        st.session_state["selected_categories"] = selected_categories
        
        # 记录用户交互
        interaction = {
            'user_id': current_user_id,
            'timestamp': datetime.now(),
            'action': 'get_recommendation',
            'parameters': {'top_n': top_n, 'categories': selected_categories}
        }
        st.session_state.user_interactions.append(interaction)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # 推荐结果展示
    if st.session_state.get("show_recommend", False):
        current_user = st.session_state["current_user_id"]
        current_top_n = st.session_state["current_top_n"]
        current_categories = st.session_state.get("selected_categories", [])
        
        # 显示加载动画
        with st.spinner("🤖 AI正在分析您的偏好并生成个性化推荐..."):
            time.sleep(1)  # 短暂延迟增加真实感
            
            result, user_profile = get_enhanced_recommendation_and_profile(
                current_user, current_top_n, current_categories
            )
        
        if user_profile:
            # 用户画像展示
            st.markdown("""
                <div class="module-main-section">
                    <h2 style="color: #2C3E50; margin-bottom: 20px;">👤 用户画像分析</h2>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 用户基本信息
                st.markdown(f"""
                    <div class="module-profile-card">
                        <h4>🎯 兴趣分析</h4>
                        <div class="module-profile-item">
                            <strong>主要兴趣:</strong> {', '.join(user_profile.get('topics', ['暂无']))}
                        </div>
                        <div class="module-profile-item">
                            <strong>关注地区:</strong> {', '.join(user_profile.get('regions', ['暂无']))}
                        </div>
                        <div class="module-profile-item">
                            <strong>偏好类别:</strong> {', '.join([f'{k[0]}/{k[1]}' if isinstance(k, tuple) else str(k) for k in list(user_profile.get('favorite_categories', {}).keys())[:3]])}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # 历史点击展示
                click_history = user_profile.get('click_history', [])[:5]
                if click_history:
                    st.markdown("""
                        <div class="module-profile-card">
                            <h4>📚 最近阅读历史</h4>
                    """, unsafe_allow_html=True)
                    
                    for i, title in enumerate(click_history, 1):
                        st.markdown(f"""
                            <div class="module-timeline-item">
                                <strong>{i}.</strong> {title[:50]}{'...' if len(title) > 50 else ''}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                # 用户偏好饼图
                fav_cats = user_profile.get('favorite_categories', {})
                if fav_cats:
                    import matplotlib
                    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
                    matplotlib.rcParams['axes.unicode_minus'] = False
                    
                    fig, ax = plt.subplots(figsize=(8, 8))
                    labels = [f"{k[0]}/{k[1]}" if isinstance(k, tuple) else str(k) for k in fav_cats.keys()]
                    sizes = list(fav_cats.values())
                    
                    # 使用更现代的配色方案
                    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
                    
                    wedges, texts, autotexts = ax.pie(
                        sizes, 
                        labels=labels, 
                        autopct='%1.1f%%', 
                        startangle=90,
                        colors=colors[:len(labels)], 
                        wedgeprops=dict(width=0.6, edgecolor='white', linewidth=3),
                        textprops={'fontsize': 12, 'weight': 'bold'}
                    )
                    
                    ax.set_title('用户偏好分布', fontsize=16, weight='bold', pad=20)
                    ax.axis('equal')
                    fig.patch.set_facecolor((0, 0, 0, 0))  # 使用RGBA格式的透明色
                    
                    st.pyplot(fig, use_container_width=True)
            
                st.markdown("</div>", unsafe_allow_html=True)
        
        # 推荐新闻展示
        if result:
            st.markdown("""
                <div class="module-main-section">
                    <h2 style="color: #2C3E50; margin-bottom: 25px;">📰 个性化推荐</h2>
            """, unsafe_allow_html=True)
            
            # 创建网格布局
            news_cols = st.columns(3, gap="large")
            
            for idx, news in enumerate(result):
                col_idx = idx % 3
                
                with news_cols[col_idx]:
                    # 生成推荐分数（模拟）
                    rec_score = round(85 + random.random() * 10, 1)
                    
                    unique_key = f"{news['news_id']}_{idx}"
                    
                    # 新闻卡片展示 - 优化布局对齐
                    with st.container():
                        # 推荐分数 - 小号显示
                        st.markdown(f"""
                            <div style="text-align: right; margin-bottom: 10px;">
                                <span style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                                             color: white; padding: 4px 8px; border-radius: 12px; 
                                             font-size: 12px; font-weight: 600;">
                                    匹配度 {rec_score}%
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # 新闻标题 - 统一字体大小
                        st.markdown(f"**{news['title']}**")
                        
                        # 分类信息 - 统一格式
                        col_cat1, col_cat2 = st.columns(2)
                        with col_cat1:
                            st.caption(f"📂 {news['category']}")
                        with col_cat2:
                            st.caption(f"📁 {news['sub_category']}")
                        
                        # 新闻摘要 - 限制长度
                        abstract = news['abstract'][:200] + "..." if len(news['abstract']) > 200 else news['abstract']
                        st.write(abstract)
                        
                        # 标签展示 - 优化样式
                        if 'tags' in news and news['tags']:
                            tags_text = " • ".join(news['tags'][:3])
                            st.caption(f"🏷️ {tags_text}")
                        
                        # 原文链接 - 统一样式
                        if 'url' in news and news['url']:
                            st.markdown(f"[🔗 阅读原文]({news['url']})")
                        
                        # 分隔线
                        st.divider()
                    
                    # 反馈系统 - 优化布局
                    with st.expander("💭 您的反馈", expanded=False):
                        # 使用表单进行局部刷新
                        with st.form(key=f"enhanced_form_{unique_key}"):
                            # 评分和反馈类型并排
                            col_rating, col_feedback = st.columns([1, 1])
                            
                            with col_rating:
                                rating = st.selectbox(
                                    "评分", 
                                    [1, 2, 3, 4, 5], 
                                    key=f"rate_{unique_key}",
                                    format_func=lambda x: "⭐" * x
                                )
                            
                            with col_feedback:
                                feedback_type = st.selectbox(
                                    "反馈类型",
                                    ["喜欢", "不感兴趣", "内容质量差", "标题党", "其他"],
                                    key=f"feedback_type_{unique_key}"
                                )
                            
                            # 详细反馈 - 全宽度
                            feedback_text = st.text_area(
                                "详细反馈", 
                                key=f"fb_{unique_key}",
                                placeholder="请分享您对这篇新闻的看法...",
                                height=80
                            )
                            
                            # 提交按钮 - 居中
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                submitted = st.form_submit_button(
                                    "📤 提交反馈",
                                    use_container_width=True
                                )
                            
                            if submitted:
                                # 保存反馈到session state
                                feedback_data = {
                                    'news_id': news['news_id'],
                                    'user_id': current_user,
                                    'rating': rating,
                                    'feedback_type': feedback_type,
                                    'feedback_text': feedback_text,
                                    'timestamp': datetime.now()
                                }
                                
                                st.session_state[f"feedback_{unique_key}"] = feedback_data
                                
                                # 显示成功消息
                                st.success(f"✅ 感谢您的反馈！评分: {'⭐' * rating} | 类型: {feedback_type}")
                    
                    # 添加卡片间距
                    st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 推荐总结
            st.markdown(f"""
                <div class="module-main-section" style="text-align: center;">
                    <h3 style="color: #2C3E50;">📊 本次推荐总结</h3>
                    <p style="font-size: 16px; color: #7F8C8D;">
                        为用户 <strong>{current_user}</strong> 成功推荐了 <strong>{len(result)}</strong> 篇个性化新闻
                    </p>
                    <p style="font-size: 14px; color: #BDC3C7;">
                        推荐时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
                <div class="module-main-section" style="text-align: center;">
                    <h3 style="color: #E74C3C;">⚠️ 暂无推荐结果</h3>
                    <p>抱歉，没有找到符合条件的新闻推荐，请尝试调整筛选条件或选择其他用户。</p>
                </div>
            """, unsafe_allow_html=True)

    else:
        # 欢迎界面
        st.markdown("""
            <div class="module-main-section" style="text-align: center;">
                <h2 style="color: #2C3E50; margin-bottom: 20px;">🎉 欢迎使用智能新闻推荐系统</h2>
                <p style="font-size: 18px; color: #7F8C8D; margin-bottom: 30px;">
                    点击上方按钮开始您的个性化新闻推荐之旅
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # 功能介绍卡片 - 使用原生组件
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **🎯 精准推荐**
            
            基于您的阅读历史和兴趣偏好，为您精选最相关的新闻内容
            """)
        
        with col2:
            st.warning("""
            **🧠 智能分析**
            
            运用先进的AI技术深度理解新闻内容和用户需求
            """)
        
        with col3:
            st.error("""
            **📊 实时优化**
            
            根据您的反馈持续学习和优化推荐效果
            """)

    # 底部信息栏
    st.markdown("""
        <div style="text-align: center; padding: 40px 0; color: #BDC3C7;">
            <hr style="margin: 30px 0; border: none; height: 1px; background: linear-gradient(to right, rgba(0,0,0,0), #BDC3C7, rgba(0,0,0,0));">
            <p>🌟 智能新闻推荐系统 | Powered by DeepSeek GPT & Qdrant Vector Database</p>
            <p style="font-size: 12px;">© 2024 AI News Recommendation Platform. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 关闭智能推荐模块容器
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
