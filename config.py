class Config:
    def __init__(self):
        from dotenv import load_dotenv, find_dotenv
        import os
        load_dotenv(find_dotenv())
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
        self.MODELS = [
            "deepseek-chat",
            "deepseek-chat-13b",
        ]
        self.DEFAULT_MODEL = self.MODELS[0]
        self.MODEL_TO_MAX_TOKENS = {
            "deepseek-chat": 4096,
            "deepseek-chat-13b": 8192,
        }
        self.EMBEDDING_MODEL = "C:/Users/guohaoyu/.cache/huggingface/hub/models--BAAI--bge-small-zh-v1.5/snapshots/7999e1d3359715c523056ef9478215996d62a620"
        self.EMBEDDING_DIMS = 512
        self.QDRANT_HOST = "localhost"
        self.QDRANT_PORT = 6333