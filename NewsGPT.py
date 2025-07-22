import openai
from loguru import logger
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
from config import Config  # 使用文档2的配置类

class DeepSeekGPT:
    def __init__(self, config: Optional[Config] = None):
        """
        重构后的初始化方法，使用统一的配置管理
        :param config: 配置对象，默认为新创建的Config实例
        """
        self.config = config or Config()
        self.client = openai.OpenAI(
            api_key=self.config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"  # DeepSeek API 端点
        )
        # 初始化本地嵌入模型
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)

    def get_completion(
            self,
            messages: Union[str, List[dict]],
            model: Optional[str] = None,
            max_tokens: int = 2000,
            temperature: float = 0.7,
            stream: bool = False,
    ) -> Union[str, openai.Stream]:
        """
        创建对话模型响应（支持单字符串和消息列表）
        
        改进点：
        1. 添加类型注解
        2. 使用配置中的默认模型
        3. 增强错误处理
        4. 优化日志格式
        """
        # 处理输入类型
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif not isinstance(messages, list):
            raise ValueError("无效的 'messages' 类型。它应该是一个字符串或消息列表")

        # 使用配置中的默认模型
        model = model or self.config.DEFAULT_MODEL

        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                stream=stream,
                temperature=temperature,
            )

            if stream:
                return response

            # 记录使用情况
            usage = response.usage
            logger.success(
                f"非流式输出 | model: {model} | total_tokens: {usage.total_tokens} "
                f"= prompt_tokens: {usage.prompt_tokens} "
                f"+ completion_tokens: {usage.completion_tokens}"
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"API请求失败: {str(e)}")
            raise

    def get_embeddings(self, input: Union[str, List[str]]) -> List[List[float]]:
        """
        创建文本嵌入向量（支持单文本和文本列表）
        
        改进点：
        1. 使用本地嵌入模型替代OpenAI API
        2. 优化批处理
        3. 添加维度验证
        """
        if isinstance(input, str):
            input = [input]
        
        # 使用本地模型生成嵌入向量
        embeddings = self.embedding_model.encode(input).tolist()
        
        # 验证维度一致性
        if embeddings and len(embeddings[0]) != self.config.EMBEDDING_DIMS:
            logger.warning(f"嵌入维度异常: 预期 {self.config.EMBEDDING_DIMS}, 实际 {len(embeddings[0])}")
        
        return embeddings


if __name__ == "__main__":
    # 测试代码
    config = Config()
    gpt = DeepSeekGPT(config)

    # 测试聊天功能
    print("\n--- 测试聊天功能 ---")
    response = gpt.get_completion("你好", temperature=0.8)
    print(f"回复: {response}")

    # 测试嵌入向量
    print("\n--- 测试嵌入向量 ---")
    texts = ["深度学习", "机器学习"]
    embeddings = gpt.get_embeddings(texts)
    
    print(f"生成 {len(embeddings)} 个嵌入向量")
    print(f"每个向量维度: {len(embeddings[0])} (预期: {config.EMBEDDING_DIMS})")