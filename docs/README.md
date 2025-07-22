# 新闻推荐系统
PS:第一个git项目，本着学习的目的，希望大家可以多多指正，多多交流，目前还有一些问题，比如脚本的显示是乱码，不过不影响正常使用
PS：因为大模型接口的问题，程序运行会有些慢，使用时可以稍等一会儿，附上首页截图：
<img width="1918" height="1041" alt="image" src="https://github.com/user-attachments/assets/64dc0fa9-cb28-4f5e-84cc-a4c81643ac91" />





基于 DeepSeek GPT 和向量数据库的个性化新闻推荐系统。

## 项目结构

```
newsDP/
├── config.py                  # 统一配置管理
├── NewsGPT.py                 # DeepSeek GPT 接口封装
├── db_qdrant.py              # Qdrant 向量数据库封装
├── save_news_to_qdrant.py    # 数据预处理和入库模块
├── utils.py                  # 推荐系统核心逻辑
├── main.py                   # 主程序入口
├── requirements.txt          # 依赖包列表
└── MIND/                     # MIND 数据集
    └── MINDsmall_train/
        ├── news.tsv          # 新闻数据
        └── behaviors.tsv     # 用户行为数据
```

## 模块职责

### 1. save_news_to_qdrant.py - 数据处理模块
- **职责**: 数据预处理、向量生成、批量入库
- **核心类**: `NewsDataProcessor`
- **主要功能**:
  - 加载和预处理新闻数据
  - 批量计算文本嵌入向量
  - 将向量数据保存到 Qdrant 数据库

### 2. utils.py - 推荐核心模块
- **职责**: 推荐算法、用户画像、向量搜索
- **核心类**: `NewsRecommender`
- **主要功能**:
  - 用户行为历史分析
  - GPT 驱动的用户画像生成
  - 向量搜索候选新闻
  - 基于用户画像的新闻排序

### 3. main.py - 主程序模块
- **职责**: 程序入口、流程控制、结果展示
- **核心类**: `NewsRecommendationApp`
- **主要功能**:
  - 数据初始化管理
  - 推荐演示模式
  - 交互式推荐模式

## 使用方法

### 1. 环境准备
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件：
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 运行系统

#### 演示模式（默认）
```bash
python main.py
```

#### 交互模式
```bash
python main.py --mode interactive
```

#### 仅数据设置
```bash
python main.py --mode setup_only
```

#### 强制重建数据库
```bash
python main.py --force-rebuild
```

### 4. 单独运行模块

#### 仅数据入库
```bash
python save_news_to_qdrant.py
```

#### 仅推荐测试
```bash
python utils.py
```

## 系统流程

1. **数据预处理**: 加载 MIND 数据集，清洗和格式化新闻数据
2. **向量化**: 使用 BGE 中文嵌入模型生成新闻向量
3. **入库**: 将向量和元数据批量存储到 Qdrant
4. **用户分析**: 基于用户点击历史生成兴趣画像
5. **候选召回**: 通过向量相似度搜索候选新闻
6. **个性化排序**: 使用 DeepSeek GPT 基于用户画像排序
7. **结果展示**: 返回个性化推荐新闻列表

## 技术栈

- **大语言模型**: DeepSeek API
- **嵌入模型**: BAAI/bge-small-zh-v1.5
- **向量数据库**: Qdrant
- **数据处理**: Pandas
- **日志系统**: Loguru

## 注意事项

1. 首次运行需要下载嵌入模型（约 100MB）
2. 确保 Qdrant 服务正在运行（默认 localhost:6333）
3. DeepSeek API Key 必须有效
4. 数据入库过程较耗时，建议耐心等待

## 扩展功能

- 支持多种推荐策略
- 可配置的嵌入模型
- 实时用户反馈学习
- 推荐效果评估指标
