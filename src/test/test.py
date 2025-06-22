import os,sys
sys.path.append(os.getcwd())

from src.config.config import Config
from src.env.env import *
from src.policy.policy import GameRule




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

    day_idx = 1
    while True:

        game_rule.night_kill()
        config.game_state["阶段"] = "白天"
        game_rule.play_round()
        game_rule.day_vote()
        game_rule.dead_list = []

        #===============================================
        '''             check completion             '''   
        #===============================================
        alive_roles = []
        for role in role_list:
            if role.name not in config.game_state["死者"]:
                alive_roles.append(role.role)
        # check if 狼人 won the game -> 获胜方式为屠边，即让神职全部出局，或让3位平民全部出局
        if "村民" not in alive_roles or ("预言家" not in alive_roles and "女巫" not in alive_roles):
            print("====================== 狼人取得胜利，游戏结束 ======================")
            break
        # check if 好人 won the game -> 狼人全部出局
        if "狼人" not in alive_roles:
            print("====================== 好人取得胜利，游戏结束 ======================")
            break
        
        day_idx += 1
        config.game_state["阶段"] = "黑夜"
        config.game_state["轮数"] = day_idx
        print("====================== 游戏继续 ======================")
        

    
if __name__=="__main__":
    main()