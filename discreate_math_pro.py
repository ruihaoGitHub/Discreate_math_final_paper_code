"""
深圳地铁智能助手高级版
该脚本演示了结合 NetworkX 图算法和 LLM Tool Calling 功能，构建图增强检索的地铁问答助手。
1. 使用 NetworkX 构建深圳地铁网络图。
2. 使用 LLM 的 Tool Calling 功能从自然语言中提取起点和终点。
3. 使用 NetworkX 计算最短路径。
4. 使用 LLM 将计算出的路径转化为自然语言回复用户。
"""

from openai import OpenAI
import json
import networkx as nx

# 初始化 OpenAI 客户端，配置 ModelScope 的 API Key 和 Base URL
client = OpenAI(
    api_key="ms-1157dcd4-bff3-4242-9c93-8e7c7f814019", # 请替换成您的ModelScope Access Token
    base_url="https://api-inference.modelscope.cn/v1/"
)

# 指定使用的模型 ID
MODEL_ID = 'Qwen/Qwen2.5-Coder-32B-Instruct' 
# 初始化一个无向图用于存储地铁网络
sz_subway = nx.Graph()

# 深圳地铁线路数据 (部分)
lines = {
    "1号线": ["罗湖", "国贸", "老街", "大剧院", "科学馆", "华强路", "岗厦", "会展中心", "购物公园", "香蜜湖", "车公庙", "竹子林", "侨城东", "华侨城", "世界之窗", "白石洲", "高新园", "深大", "桃园", "大新", "鲤鱼门", "前海湾", "新安", "宝安中心", "宝体", "坪洲", "西乡", "固戍", "后瑞", "机场东"],
    "2号线": ["赤湾", "蛇口港", "海上世界", "水湾", "东角头", "湾厦", "海月", "登良", "后海", "科苑", "红树湾", "世界之窗", "侨城北", "深康", "安托山", "侨香", "香蜜", "香梅北", "景田", "莲花西", "福田", "市民中心", "岗厦北", "华强北", "燕南", "大剧院", "湖贝", "黄贝岭", "新秀", "莲塘口岸", "仙湖路", "莲塘"],
    "3号线": ["福保", "益田", "石厦", "购物公园", "福田", "少年宫", "莲花村", "华新", "通新岭", "红岭", "老街", "晒布", "翠竹", "田贝", "水贝", "草埔", "布吉", "木棉湾", "大芬", "丹竹头", "六约", "塘坑", "横岗", "永湖", "荷坳", "大运", "爱联", "吉祥", "龙城广场", "南联", "双龙"],
    "4号线": ["福田口岸", "福民", "会展中心", "市民中心", "少年宫", "莲花北", "上梅林", "民乐", "白石龙", "深圳北站", "红山", "上塘", "龙胜", "龙华", "清湖", "清湖北", "竹村", "茜坑", "长湖", "观澜", "松元厦", "观澜湖", "牛湖"],
    "5号线": ["赤湾", "荔湾", "铁路公园", "妈湾", "前海湾", "临海", "宝华", "宝安中心", "翻身", "灵芝", "洪浪北", "兴东", "留仙洞", "西丽", "大学城", "塘朗", "长岭陂", "深圳北站", "民治", "五和", "坂田", "杨美", "上水径", "下水径", "长龙", "布吉", "百鸽笼", "布心", "太安", "怡景", "黄贝岭"],
    "6号线": ["科学馆", "通新岭", "体育中心", "八卦岭", "银湖", "翰岭", "梅林关", "深圳北站", "红山", "上芬", "元芬", "阳台山东", "官田", "上屋", "长圳", "凤凰城", "光明大街", "光明", "科学公园", "楼村", "红花山", "公明广场", "合水口", "薯田埔", "松岗公园", "溪头", "松岗"],
    "9号线": ["前湾", "梦海", "怡海", "荔林", "南油西", "南油", "南山书城", "深大南", "粤海门", "高新南", "红树湾南", "深湾", "深圳湾公园", "下沙", "车公庙", "香梅", "景田", "梅景", "下梅林", "梅村", "上梅林", "孖岭", "银湖", "泥岗", "红岭北", "园岭", "红岭", "红岭南", "鹿丹村", "人民南", "向西村", "文锦"],
    "11号线": ["碧头", "松岗", "后亭", "沙井", "马安山", "塘尾", "桥头", "福永", "机场北", "机场", "碧海湾", "宝安", "前海湾", "南山", "后海", "红树湾南", "车公庙", "福田", "岗厦北"]
}

print("正在构建地铁网络...")
# 遍历所有线路，将相邻站点作为边添加到图中
for line_name, stations in lines.items():
    for i in range(len(stations) - 1):
        sz_subway.add_edge(stations[i], stations[i+1], line=line_name, weight=1)


def get_route_from_graph(start, end):
    """
    使用 NetworkX 计算两个站点之间的最短路径
    
    Args:
        start (str): 起点站名
        end (str): 终点站名
        
    Returns:
        list or str: 成功时返回站点列表，失败时返回错误信息
    """
    try:
        start = start.replace("站", "").strip()
        end = end.replace("站", "").strip()
        # 使用 Dijkstra 算法 (默认) 计算最短路径
        path = nx.shortest_path(sz_subway, source=start, target=end, weight='weight')
        return path
    except nx.NetworkXNoPath:
        return "无法到达"
    except nx.NodeNotFound as e:
        return f"站点名称错误: {e}" 

def format_route_with_direction(path):
    """
    将站点列表格式化为带有线路和方向的描述字符串
    
    Args:
        path (list): 站点列表
        
    Returns:
        str: 格式化后的路径描述
    """
    if not isinstance(path, list) or len(path) < 2:
        return str(path)
    description = []
    for i in range(len(path) - 1):
        curr_s = path[i]
        next_s = path[i+1]
        target_line = None
        direction = None
        # 查找连接当前两站的线路和方向
        for line_name, stations in lines.items():
            if curr_s in stations and next_s in stations:
                idx_curr = stations.index(curr_s)
                idx_next = stations.index(next_s)
                if abs(idx_curr - idx_next) == 1:
                    target_line = line_name
                    if idx_next > idx_curr:
                        direction = stations[-1]
                    else:
                        direction = stations[0]
                    break
        if target_line:
            description.append(f"{curr_s} -> {next_s} [{target_line} 往 {direction}]")
    return "\n".join(description)

def ask_llm_extract_stations_with_tool(user_query):
    """
    使用 LLM 的 Tool Calling 功能，从自然语言中提取起点和终点
    保证返回结果是可靠的 JSON 格式
    
    Args:
        user_query (str): 用户的输入
        
    Returns:
        dict: 包含 'start' 和 'end' 的字典，提取失败返回空字典
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{'role': 'user', 'content': user_query}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "extract_stations",
                        "description": "从用户的文本中提取地铁出行的起点和终点",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "start": {
                                    "type": "string",
                                    "description": "出行的起点站名, e.g. 粤海门"
                                },
                                "end": {
                                    "type": "string",
                                    "description": "出行的终点站名, e.g. 红树湾南"
                                }
                            },
                            "required": ["start", "end"]
                        }
                    }
                }
            ],
            tool_choice={"type": "function", "function": {"name": "extract_stations"}}
        )
        
        message = response.choices[0].message
        
        # 解析 Tool Call 返回的参数
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            
            if tool_call.function.name == "extract_stations":
                arguments_json_str = tool_call.function.arguments
                return json.loads(arguments_json_str)


    except Exception as e:
        print(f"使用 Tool Calling 提取地点出错: {e}")
    
    return {}

def ask_llm_generate_reply(user_query, route_list):
    """
    将计算出的路径信息，通过 LLM 转化为自然语言回复用户
    
    Args:
        user_query (str): 用户原始问题
        route_list (str): 格式化后的路径信息
    """
    prompt = f"""
    用户问：{user_query}
    系统计算出的路线：
    {route_list}
    
    请根据路线，用简洁、友好的语气回答用户。
    注意：这是确定性的路线，如果地点都是同一号地铁线上的站点就省略中间的站点，其余不要自己发挥，只负责转述。
    """
    
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ],
        stream=True
    )
    for chunk in response:
        print(chunk.choices[0].delta.content, end='', flush=True)


if __name__ == "__main__":
    print(f"--- 深圳地铁智能助手(高级版)  ---")
    
    while True:
        user_input = input("\n请问您从哪去哪儿 (输入 q 退出): ")
        if user_input.lower() in ['q', 'quit', '退出']:
            break
        if not user_input.strip():
            continue

        print(f"用户提问: {user_input}")
        
        # 1. 提取地点
        locations = ask_llm_extract_stations_with_tool(user_input)
        print(f"ai 提取地点: {locations}")
        
        start = locations.get("start")
        end = locations.get("end")
        
        if start and end:
            # 2. 计算路径
            real_route_list = get_route_from_graph(start, end)
            
            if isinstance(real_route_list, list):
                # 3. 格式化路径
                detailed_route_info = format_route_with_direction(real_route_list)
            else:
                detailed_route_info = real_route_list 
            
            # 4. 生成回复
            ask_llm_generate_reply(user_input, detailed_route_info)
        else:
            print("没听懂你想去哪，请再说清楚一点...")
        print('')