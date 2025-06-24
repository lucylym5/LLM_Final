import random
import os,sys

sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')
sys.path.append(os.getcwd()+'/../../')

from typing import *

from src.config.config import Config

class Role:
    def __init__(self, name:str, role:str, model):
        self.name = name # 玩家编号
        self.role = role # 玩家角色
        self.message = []
        self.model = model
        self.memory = [] # 玩家记忆
        
    def build_wolf_prompt(self):
        return (
            f"你是{self.name}，请和同伴协商今晚要杀谁。当场上预言家和女巫均死亡，或3名村民全部死亡，你们将获得胜利。\n"
            f"这是之前所有人的全部聊天记录：\n" + "\n".join(self.memory) +
            f"\n请你据此继续表达意见。请在发言最后明确写出“我认为应该杀玩家X”，其中X为序号。"
        )
    
    def build_prompt(self,game_state):
        return(
            f"你是{self.name}，这是第{game_state['轮数']}天白天。\n"
            f"昨晚死亡角色：{', '.join(game_state['死者'])}。"
            f"这是之前所有人的全部聊天记录: \n" + "\n".join(self.memory) + 
            "\n请你据此继续发言，说明你的判断、你怀疑或相信的人，或澄清自己的身份。"
        )
    def last_words(self):
        return(
            f"你是{self.name}，你昨天晚上死了。\n"
            f"这是之前所有人的全部聊天记录: \n" + "\n".join(self.memory) + 
            "\n请你据此发表遗言，帮助你的阵营赢得游戏。"
        )
    
    def vote_prompt(self,game_state):
        return(
            f"你是{self.name}，昨晚死亡角色：{', '.join(game_state['死者'])}。\n"
            f"这是之前所有人的全部行动记录: \n" + "\n".join(self.memory) + 
            f"请投票决定活着的玩家中你最希望谁出局。请直接说出你要投票的玩家名(例如玩家1)，不要说任何其他内容。\n"
        )
    
    def again_prompt(self):
        return(
            f"你是{self.name}，目前投票中得票最多但出现平票。"
            f"\n这是之前所有人的全部行动记录: \n" + "\n".join(self.memory) + 
            f"请据此为自己辩护。\n"
        )
    
    def again_vote(self,top_candidates):
        return(
            f"你是{self.name}，目前投票候选人：{', '.join(top_candidates)}。\n"
            f"这是之前所有人的全部行动记录: \n" + "\n".join(self.memory) + 
            f"请据此投票决定候选人中你最希望谁出局。请直接说出你要投票的玩家名，不要说任何其他内容。\n"
        )
    
    def check_prompt(self):
        return(
            f"这是之前的全部游戏记录：\n" + "\n".join(self.memory) +
            f"你是预言家，你可以随机选择一个玩家查验他是好人还是坏人。请直接说出你想查验的玩家名（格式：玩家X）。注意，不要说理由，直接说出玩家名（格式：玩家X）"
        )

    #生成回答
    def generate_response(self, prompt):
        model = self.model
        system = Config.role_system_prompts.get(self.name)
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": Config.rule_prompts},
                    {"role": "assistant", "content": "我已经清楚了本次狼人杀的游戏规则和自己的角色，可以开始游戏。"},
                    {"role": "user", "content": prompt}]
        response = model.chat.completions.create(
            model = "deepseek-chat" if "deepseek" in str(model.base_url) else "qwen-plus",
            messages = messages,
            max_tokens=1024
        )
        reply = response.choices[0].message.content.strip()
        return reply
    


class BaseEnv:
    def __init__(self,
                 config:Config,
                 count_s = 0,
                 count_p = 0):
        self.config = config
        self.role_identity = self.config.role_identity
        self.role_models = self.config.role_models
        self.count_s = count_s
        self.count_p = count_p
        self.speak_seq = []

    def setup(self):
        role_list = []
        for name in self.role_identity.keys():
            if self.role_models.get(name) is not None:
                role = Role(name=name,
                            role=self.role_identity.get(name),
                            model=self.role_models.get(name))
            else:
                role = Role(name=name,
                            role=self.role_identity.get(name),
                            model=None)
            role_list.append(role)
        speak_seq = random.sample(role_list, k=len(role_list))
        self.config.game_state["发言顺序"] = speak_seq
        
        return role_list