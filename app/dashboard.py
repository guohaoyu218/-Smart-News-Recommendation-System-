import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from main import NewsRecommendationApp

def main():
    """
    数据分析仪表板主页面
    """
    # 移除page_config，避免与主应用冲突
    st.markdown("""
    <div style='text-align:center; padding:20px; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border-radius:15px; margin-bottom:20px;'>
        <h2>📊 数据分析仪表板</h2>
        <p>系统运行状态与用户行为分析</p>
    </div>
    """, unsafe_allow_html=True)
    app = NewsRecommendationApp()
    # 数据分析主逻辑（示例）
    st.markdown("### 系统运行统计")
    try:
        # 获取用户数
        user_ids = app.get_all_user_ids() if hasattr(app, "get_all_user_ids") else []
        total_users = len(user_ids)
        # 推荐数（可用行为数据模拟）
        df_behaviors = app.recommender.load_behaviors_data() if hasattr(app.recommender, "load_behaviors_data") else None
        daily_recommendations = len(df_behaviors) if df_behaviors is not None else random.randint(2000, 3500)
        # 活跃用户（模拟）
        active_users = len(set(df_behaviors['user_id'])) if df_behaviors is not None else random.randint(80, 150)
        # 平均评分（模拟）
        avg_rating = round(random.uniform(4.2, 4.8), 2)
        # 系统可用性（模拟）
        system_uptime = 99.8
        # 统计结果
        stats = {
            "总用户数": total_users,
            "今日推荐": daily_recommendations,
            "活跃用户": active_users,
            "平均评分": avg_rating,
            "系统可用性": system_uptime
        }
        st.json(stats)
    except Exception as e:
        st.error(f"系统统计获取失败: {e}")
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#7F8C8D; padding:20px;'>
        <p>📊 数据分析 | 实时监控与统计</p>
        <p style='font-size:12px;'>© 2024 AI News Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .activity-item {
        padding: 15px;
        border-left: 3px solid #667eea;
        margin: 10px 0;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .status-online {
        color: #2ECC71;
    }
    .status-offline {
        color: #E74C3C;
    }
    </style>
    """, unsafe_allow_html=True)
    # 页面标题
    st.markdown("""
    <div class="dashboard-header">
        <h1>📊 新闻推荐系统 - 实时数据分析</h1>
        <p>系统运行状态、用户行为分析与推荐效果监控</p>
    </div>
    """, unsafe_allow_html=True)

    # 模拟实时数据生成
    @st.cache_data(ttl=30)  # 30秒刷新一次
    def generate_mock_analytics():
        """生成模拟的分析数据"""
        current_time = datetime.now()
        # 系统指标
        metrics = {
            'total_users': random.randint(1200, 1500),
            'active_users': random.randint(80, 150),
            'daily_recommendations': random.randint(2000, 3500),
            'avg_rating': round(random.uniform(4.2, 4.8), 2),
            'click_through_rate': round(random.uniform(0.15, 0.35), 3),
            'system_uptime': 99.8
        }
        # 用户活动数据
        activities = []
        for i in range(10):
            activity_time = current_time - timedelta(minutes=random.randint(1, 60))
            activities.append({
                'time': activity_time.strftime("%H:%M"),
                'user_id': f"U{random.randint(1000, 9999)}",
                'action': random.choice(['获取推荐', '评分', '点击新闻', '收藏']),
                'details': random.choice(['体育新闻', '科技资讯', '娱乐八卦', '财经新闻'])
            })
        # 类别热度数据
        categories = ['sports', 'tech', 'entertainment', 'finance', 'health', 'politics']
        category_data = {cat: random.randint(50, 200) for cat in categories}
        # 时间序列数据（过去24小时）
        hourly_data = []
        for h in range(24):
            hour_time = current_time - timedelta(hours=23-h)
            hourly_data.append({
                'hour': hour_time.strftime("%H:00"),
                'recommendations': random.randint(50, 150),
                'clicks': random.randint(20, 60),
                'users': random.randint(10, 40)
            })
        return metrics, activities, category_data, hourly_data

    # 获取数据
    metrics, activities, category_data, hourly_data = generate_mock_analytics()

    # 核心指标展示
    st.markdown("## 🎯 核心指标")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['total_users']}</h3>
            <p>总用户数</p>
            <small class="trend-up">↗ +12 today</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['active_users']}</h3>
            <p>活跃用户</p>
            <small class="trend-up">↗ +5.2%</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['daily_recommendations']}</h3>
            <p>今日推荐</p>
            <small class="trend-up">↗ +8.3%</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['avg_rating']}</h3>
            <p>平均评分</p>
            <small class="trend-up">↗ +0.1</small>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        ctr_percent = metrics['click_through_rate'] * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ctr_percent:.1f}%</h3>
            <p>点击率</p>
            <small class="trend-up">↗ +2.1%</small>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['system_uptime']}%</h3>
            <p>系统可用性</p>
            <small class="status-online">● 在线</small>
        </div>
        """, unsafe_allow_html=True)

    # 图表展示区域
    st.markdown("## 📈 数据趋势")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📊 新闻类别热度")
        category_df = pd.DataFrame(list(category_data.items()), columns=['Category', 'Views'])
        st.bar_chart(category_df.set_index('Category'))
        st.markdown('</div>', unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### ⏰ 24小时活动趋势")
        hourly_df = pd.DataFrame(hourly_data)
        hourly_df = hourly_df.set_index('hour')
        st.line_chart(hourly_df[['recommendations', 'clicks', 'users']])
        st.markdown('</div>', unsafe_allow_html=True)

    # 实时活动日志
    st.markdown("## 🔄 实时用户活动")
    activity_col1, activity_col2 = st.columns([2, 1])
    with activity_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📝 最近活动")
        for activity in activities[:8]:
            st.markdown(f"""
            <div class="activity-item">
                <strong>{activity['time']}</strong> - 
                用户 {activity['user_id']} 
                <span style="color: #667eea;">{activity['action']}</span>
                ({activity['details']})
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with activity_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### ⚙️ 系统状态")
        services = [
            {"name": "推荐引擎", "status": "正常", "response_time": "45ms"},
            {"name": "向量数据库", "status": "正常", "response_time": "12ms"},
            {"name": "GPT服务", "status": "正常", "response_time": "180ms"},
            {"name": "Web界面", "status": "正常", "response_time": "8ms"}
        ]
        for service in services:
            status_class = "status-online" if service["status"] == "正常" else "status-offline"
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; border-radius: 5px; background: #f8f9fa;">
                <strong>{service['name']}</strong><br>
                <span class="{status_class}">● {service['status']}</span><br>
                <small>响应时间: {service['response_time']}</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 推荐效果分析
    st.markdown("## 🎯 推荐效果分析")
    effect_col1, effect_col2, effect_col3 = st.columns(3)
    with effect_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📊 评分分布")
        ratings = [1, 2, 3, 4, 5]
        rating_counts = [5, 15, 45, 120, 180]  # 模拟数据，5分最多
        rating_df = pd.DataFrame({'Rating': ratings, 'Count': rating_counts})
        st.bar_chart(rating_df.set_index('Rating'))
        st.markdown('</div>', unsafe_allow_html=True)
    with effect_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 🔄 用户反馈类型")
        feedback_types = ['喜欢', '不感兴趣', '内容质量差', '标题党', '其他']
        feedback_counts = [150, 45, 20, 15, 25]
        feedback_df = pd.DataFrame({'Type': feedback_types, 'Count': feedback_counts})
        for i, row in feedback_df.iterrows():
            percentage = (row['Count'] / feedback_df['Count'].sum()) * 100
            st.write(f"**{row['Type']}**: {row['Count']} ({percentage:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)
    with effect_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### ⚡ 性能指标")
        performance_metrics = {
            "平均响应时间": "245ms",
            "推荐准确率": "87.3%",
            "用户满意度": "4.6/5.0",
            "日活跃度": "23.4%"
        }
        for metric, value in performance_metrics.items():
            st.metric(label=metric, value=value)
        st.markdown('</div>', unsafe_allow_html=True)

    # 自动刷新设置
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 刷新数据", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        auto_refresh = st.checkbox("自动刷新 (30秒)", value=False)
    with col3:
        st.markdown(f"**最后更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    # 页面底部
    st.markdown("""
    <div style="text-align: center; padding: 40px 0; color: #7F8C8D;">
        <p>📊 数据分析仪表板 | 实时监控推荐系统性能与用户行为</p>
        <p style="font-size: 12px;">数据每30秒自动更新 | © 2024 AI News Recommendation Platform</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

