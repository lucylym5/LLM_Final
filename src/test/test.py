import os,sys
sys.path.append(os.getcwd())

from src.config.config import Config
from src.env.env import *
from src.policy.policy import GameRule

import random
from openai import OpenAI
from collections import Counter



def main():
    #===============================================
    '''           Create Environment             '''   
    #===============================================
    config = Config()
    env = BaseEnv(config=config,
                  count_s=0,
                  count_p=0)
    role_list = env.setup()

    game_rule = GameRule(config=config,
                         env=env,
                         role_list=role_list)
    #===============================================
    '''                Game Start               '''   
    #=============================================== 
    print(f"你好，欢迎来到狼人杀互动创作空间，下面你将参与一场狼人杀游戏。\n"+f"你的用户名是{config.user_role}，身份为{config.role_identity.get(config.user_role)}。游戏开始。\n")

    game_rule.night_kill()
    config.game_state["阶段"] = "白天"
    game_rule.play_round()
    game_rule.day_vote()
    
if __name__=="__main__":
    main()