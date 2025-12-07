# 深圳地铁智能助手 (Shenzhen Metro AI Assistant)

*一个基于知识图谱与大语言模型的离散数学课程期末项目*

本项目以“深圳地铁路线查询”为应用场景，实现了一个经典的**图增强检索（Graph-RAG）** 架构，解决了大模型在处理精确、结构化任务时可能“一本正经地胡说八道”的问题。(base版本直接调用api，会胡说八道，pro版本是图增强检索，准确回答)

## 快速开始

请按照以下步骤在你的本地环境中运行本项目。

### 1. 环境配置

首先，克隆本仓库到你的本地：
```bash
git clone https://github.com/ruihaoGitHub/Discreate_math_final_paper_code.git
cd Discreate_math_final_paper_code
```

然后，安装所需的 Python 依赖库：
```bash
pip install networkx openai
```
*(建议创建一个独立的 Python 虚拟环境)*

### 2. 配置 API 密钥

> **⚠️ 重要提示：配置 API 密钥**
>
> 本项目需要调用**魔搭社区（ModelScope）** 提供的大模型 API 服务来驱动语言理解和生成模块。该服务对个人开发者**免费**，但需要你进行注册并获取 `Access Token` (即 API Key)。

请按照以下步骤获取并配置你的密钥：

1.  访问 [ModelScope 个人访问令牌页面](https://modelscope.cn/my/myaccesstoken)。
2.  使用你的淘宝/阿里云账号登录或注册一个新账号。
3.  **【关键】** 根据页面提示，**确保你的魔搭账号已经成功绑定了阿里云账号**（通常需要进行实名认证），否则 API 调用会失败。
4.  复制页面上生成的 `Access Token`。
5.  打开项目中的 `discreate_math.py` 文件，找到以下代码行：

    ```python
    # 请在这里填入你的魔搭 SDK Token
    api_key='你的_MODELSCOPE_API_KEY_在这里', 
    ```
6.  将 `'你的_MODELSCOPE_API_KEY_在这里'` 替换为你刚刚复制的 `Access Token`。

### 3. 运行程序

一切准备就绪后，在你的终端中运行主程序：

```bash
python discreate_math.py
```

## 使用示例

程序启动后，你就可以开始向它提问了：

```console
(venv) D:\> python discreate_math.py
正在构建地铁网络...
--- 深圳地铁智能助手 ---

请问您从哪去哪儿 (输入 q 退出): 从粤海门去红树湾南怎么走？
用户提问: 从粤海门去红树湾南怎么走？

>>>> 回答:
您好！从粤海门到红树湾南，推荐您按以下路线乘坐：

1.  在 **粤海门站** 乘坐 **9号线** (往文锦方向)。
2.  经过2站，在 **红树湾南站** 下车即可。

希望这段信息对您有帮助！