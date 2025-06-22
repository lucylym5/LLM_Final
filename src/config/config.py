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

    role_system_prompts= {
        "玩家2": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家2，请牢记自己的玩家序号。身份是拥有查验能力的预言家，要带领村民识别狼人。" ,
        "玩家3": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家3，请牢记自己的玩家序号。身份是谨慎的女巫，善于观察语言逻辑判断救毒时机。",
        "玩家4": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家4，请牢记自己的玩家序号。身份是狡猾而冷静的狼人，擅长伪装和引导。你的狼队友是玩家1。",
        "玩家5": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家5，请牢记自己的玩家序号。身份是村民，紧张但希望帮助大家识破狼人。",
        "玩家6": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家6，请牢记自己的玩家序号。身份是普通村民，推理不一定严谨，但会尽力思考。",
        "玩家7": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家7，请牢记自己的玩家序号。身份是观察细致的村民，擅长发现逻辑漏洞。",
    }

    game_state={
        "阶段":"白天",
        "轮数":1,
        "死者": [],
        "发言顺序": []
    }

    round_num = 3

