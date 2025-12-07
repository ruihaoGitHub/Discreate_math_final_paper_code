"""
深圳地铁智能助手基础版
该脚本演示了直接调用大语言模型 (LLM) API 来构建一个地铁问答助手。
使用了 ModelScope 的 API 服务，模型为 Qwen2.5-Coder-32B-Instruct。
"""

from openai import OpenAI

# 初始化 OpenAI 客户端，配置 ModelScope 的 API Key 和 Base URL
client = OpenAI(
    api_key="ms-1157dcd4-bff3-4242-9c93-8e7c7f814019", # 请替换成您的ModelScope Access Token
    base_url="https://api-inference.modelscope.cn/v1/"
)

# 指定使用的模型 ID
MODEL_ID = 'Qwen/Qwen2.5-Coder-32B-Instruct' 

def ask_llm_generate_reply(user_query):
    """
    调用 LLM 生成回复并流式输出
    
    Args:
        user_query (str): 用户的输入问题
    """
    # 构建提示词 (Prompt)
    prompt = f"""
    用户问：{user_query}
    请用简洁、友好的语气回答用户
    """

    # 发起流式对话请求
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ],
        stream=True
    )
    
    # 逐块打印返回的内容，实现打字机效果
    for chunk in response:
        print(chunk.choices[0].delta.content, end='', flush=True)



if __name__ == "__main__":
    print(f"--- 深圳地铁智能助手(基础版)  ---")
    
    # 进入主循环，持续接收用户输入
    while True:
        user_input = input("\n请问您从哪去哪儿 (输入 q 退出): ")
        
        # 检查退出条件
        if user_input.lower() in ['q', 'quit', '退出']:
            break
        
        # 忽略空输入
        if not user_input.strip():
            continue

        print(f"用户提问: {user_input}")
        # 调用函数生成并打印回复
        ask_llm_generate_reply(user_input)
        print('')
       