import os
import random
from openai import OpenAI

# 加载规则文档
def load_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path): #读取文件夹中的所有.txt文件
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r',encoding='utf-8') as file:
                documents.append(file.read()) #将文件内容读取为字符串添加到列表中
    return documents

rule = load_documents("./")


class Config:
    user_role = "玩家1"

    role_names=[f"玩家{i}"for i in range(2,8)]

    # 玩家身份字典
    role_identity = {
        "玩家1": "狼人",
        "玩家2": "预言家",
        "玩家3": "女巫",
        "玩家4": "狼人",
        "玩家5": "村民",
        "玩家6": "村民",
        "玩家7": "村民",
    }

    role_models={
        "玩家2": OpenAI(api_key="sk-c29297e3a3d2470a93d7833bbeacc96b", base_url="https://api.deepseek.com"),
        "玩家3": OpenAI(api_key="sk-8d94bdf8365844798f987bafd32ef2fc", base_url="https://api.deepseek.com"),
        "玩家4": OpenAI(api_key="sk-e5f37a9b2cea45069adbc7d603d4ad79", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "玩家5": OpenAI(api_key="sk-8cff54c6f47e4acfa7bb3ad4c3449918", base_url="https://api.deepseek.com"),
        "玩家6": OpenAI(api_key="sk-1e421593280e4733839b577c5de37d54", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "玩家7": OpenAI(api_key="sk-c29297e3a3d2470a93d7833bbeacc96b", base_url="https://api.deepseek.com"),
    }

    role_system_prompts= {}
    
    # 规则提示
    rule_prompts=(
        f"请仔细查看规则{rule}。特别注意，本场游戏中共有7个玩家，其中有3个村民、1个预言家、1个女巫、2个狼人，没有其他角色。游戏中没有上警等特殊规则。"
         "游戏中女巫可以使用解药救自己。女巫只有1瓶解药和1瓶毒药，用完即止。如果女巫死亡，则剩余药品将会作废，不能继续使用。"
         "无论是在进行私聊还是公开发言时，不要编造不存在的发言记录。"
         "一定要注意伪装自己，避免在公开发言中暴露自己的身份！"
    )

    game_state={
        "阶段":"黑夜",
        "轮数":1,
        "死者": [],
        "发言顺序": []
    }

    round_num = 3

