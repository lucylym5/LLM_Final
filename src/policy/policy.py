import os,sys
sys.path.append(os.getcwd())

from src.config.config import *
from src.env.env import *

class GameRule:
    def __init__(self,
                 config:Config,
                 env:BaseEnv,
                 role_list:List[Role]):
        self.config = config
        self.env = env
        self.role_list = role_list
        self.dead_list = []
        self.alive_list = []
        self.game_state = self.config.game_state
        self.count_s = self.env.count_s
        self.count_p = self.env.count_p

    # 夜晚狼人协商
    def night_kill(self):
        user_role = self.config.user_role
        # get wolves role
        wolves = []
        for role in self.role_list:
            if role.role == "狼人" and role.name not in self.game_state["死者"]:
                wolves.append(role)
        
        wolf_log = []

        print("\n======= 狼人夜间密谋环节 =======")
        for role in self.role_list:
            if role.role == "狼人":
                role.memory.append(f"以下为你和狼队友夜间密谋的聊天记录:")


        for round_num in range(self.config.round_num):
            print(f"\n--- 第{round_num}轮协商 ---")
            for wolf_role in wolves:
                if wolf_role.name == user_role:
                    user_input = input(f"你是狼人，请输入你的行动建议（例：……我认为应该杀玩家X。）：我认为应该杀玩家")
                    wolf_log.append(f"{user_role}：{user_input}")
                    for role in self.role_list:
                        if role.role == "狼人":
                            role.memory.append(f"{user_role}：{user_input}")
                else:
                    prompt = wolf_role.build_wolf_prompt()
                    reply = wolf_role.generate_response(prompt)
                    print(f"{wolf_role.name}：{reply}")
                    wolf_log.append(f"{wolf_role.name}：{reply}")
                    for role in self.role_list:
                        if role.name == "狼人":
                            role.memory.append(f"{wolf_role.name}：{reply}")
            
            # 每轮协商结果统计
            last_votes = {}
            for line in reversed(wolf_log):
                for wolf_role in wolves:
                    if line.startswith(f"{wolf_role.name}：") and "我认为应该杀" in line:
                        if wolf_role.name not in last_votes:
                            target = line.split("我认为应该杀")[-1].strip().rstrip("。.!！")
                            last_votes[wolf_role.name] = target
            vote_counts = Counter(last_votes.values())
            max_vote = max(vote_counts.values())
            top_targets = [k for k, v in vote_counts.items() if v == max_vote]
            if len(top_targets) == 1:
                target = top_targets[0]
                print(f"狼人已达成共识，击杀目标为：{target}")
                break
            else:
                if round_num == 2:
                    target = random.choice(top_targets)
                    print(f"狼人意见不一，平票中随机选择，击杀目标为：{target}")

        print(f"[夜晚] 狼人杀死了：{target}\n")
        for role in self.role_list:
            if role.name == "狼人":
                role.memory.append(f"狼人密谋结束，你们决定杀{target}")

        # 预言家查验
        alive_roles = []
        for role in self.role_list:
            if role.name not in self.game_state["死者"]:
                alive_roles.append(role)
        for role in alive_roles:
            if role.role == "预言家":
                if role.name == user_role:
                    user_input = input(f"{role.name}，你是预言家，请输入你要查验的人(请填写 玩家+序号):")
                    if "狼人" in self.config.role_identity.get(user_input):
                        identity = "坏人"
                    else:
                        identity = "好人"
                    print(f"{user_input}是{identity}")

                else:
                    reply=role.generate_response(role.check_prompt())
                    if "狼人" in self.config.role_identity.get(reply):
                        identity = "坏人"
                    else:
                        identity = "好人"
                    print(f"预言家{role.name}进行了查验，{reply}是{identity}")
                    role.memory.append(f"你作为预言家，在第{self.game_state['轮数']}天晚上查验了{reply}，他是{identity}")


        # 女巫用药（注意前面有两个全局变量count_s, count_p）
        for role in alive_roles:
            if role.role == "女巫":
                if role.name == user_role:
                    if self.count_s == 0:
                        user_input = input(f"{role.name}，你是女巫，今天晚上死的人是：{target}，你要救吗？是/否")
                        if user_input == "否":
                            self.game_state["死者"].append(target)
                        else:
                            self.count_s += 1
                            continue
                    if self.count_p == 0:
                        user_input = input(f"你要使用毒药吗？是/否")
                        if user_input == "是":
                            poison = input(f"你要毒的人是？（例：玩家X）")
                            self.game_state["死者"].append(poison)
                            self.count_p += 1
                        else:
                            break                  
                else:
                    if self.count_s == 0:
                        prompt1 = f"这是之前的全部游戏记录：\n" + f"\n".join(role.memory) + f"今天晚上{target}死了，你要救他吗？请直接回答 是/否，不要加标点。"
                        choice = role.generate_response(prompt1)
                        if choice == "否":
                            self.game_state["死者"].append(target)
                            role.memory.append(f"你是女巫，在第{self.game_state['轮数']}天晚上{target}死了，你没有使用解药救他。")
                            print(f"女巫{role.name}没有使用解药")
                        else:
                            self.count_s += 1
                            role.memory.append(f"你是女巫，在第{self.game_state['轮数']}天晚上{target}死了，你使用解药救了他。")
                            print(f"女巫{role.name}使用解药救了{target}")
                            continue
                    if self.count_p == 0:
                        prompt2 = f"这是之前的全部游戏记录：\n" + f"\n".join(role.memory) + f"请问你要使用毒药吗？请直接回答是/否，不要加标点。"
                        choice = role.generate_response(prompt2)
                        if choice == "是":
                            prompt3 = f"这是之前的全部游戏记录：\n" + f"\n".join(role.memory) + f"你决定使用毒药，请问你要毒杀的玩家是谁？请直接回答玩家名（例如：玩家X），不要加标点。"
                            poison =  role.generate_response(prompt3)
                            print()
                            self.game_state["死者"].append(poison)
                            role.memory.append(f"在第{self.game_state['轮数']}天晚上你使用了毒药，毒死了{poison}。")
                            print(f"女巫{role.name}使用毒药毒死了{poison}")
                            self.count_p += 1
                        else:
                            role.memory.append(f"在第{self.game_state['轮数']}天晚上你没有使用毒药。")
                            print(f"女巫{role.name}没有使用毒药")
                            break

        # 公布死亡情况
        print(f"[夜晚结束] 今夜死亡名单：{self.game_state['死者']}")
        for role in self.role_list:
            role.memory.append(f"[夜晚结束] 今夜死亡名单：{self.game_state['死者']}")
            if role.name in self.game_state["死者"]:
                self.dead_list.append(role)
        # update alive list
        self.alive_list = alive_roles.copy()




    # 发言轮
    def play_round(self):
        print(f"\n======= 第{self.game_state['轮数']}天 {self.game_state['阶段']} =======")
        for role in self.role_list:
                role.memory.append(f"天亮了，下面开始第{self.game_state['轮数']}天 {self.game_state['阶段']}的发言：")
        if self.game_state["轮数"] == 1:
            print(f"\n--- 死者发表遗言 ---")
            for role in self.role_list:
                role.memory.append(f"以下为死者发表遗言环节：")
            for role in self.dead_list:
                if role.name == self.config.user_role:
                    user_input = input(f"您是{role.name}，昨天晚上您死了，请发表遗言")
                    self.append_memory(f"{role.name}的遗言是：{user_input}")
                else:
                    reply = role.generate_response(role.last_words())
                    print(f"{role.name}：{reply}")
                    self.append_memory(f"{role}的遗言是：{reply}")
            self.append_memory(f"死者遗言发表结束，其余玩家开始发言:")

        for role in self.game_state["发言顺序"]:
            if role.name in self.game_state["死者"]:
                print(f"【{role.name}已死亡，跳过发言】")
                continue
            if role.name == self.config.user_role:
                user_input = input(f"你是{self.config.user_role}，请输入你的发言：")
                self.append_memory(f"{role.name}：{user_input}")
            else:
                prompt = role.build_prompt(self.game_state)
                reply = role.generate_response(prompt)
                print(f"{role.name}：{reply}")
                self.append_memory(f"{role.name}：{reply}")
    
       
    # 投票环节
    def day_vote(self):
        alive_roles = self.alive_list
        print(f"\n======= 投票环节 =======")
        self.append_memory(f"发言环节结束，现在开始投票")
        votes = {}
        for role in alive_roles:
            if role.name == self.config.user_role:
                vote = input(f"你是{self.config.user_role}，请输入你要投票的对象：")
                votes[vote] = votes.get(vote, 0) + 1
                self.append_memory(f"{role.name} 投票给 {vote}")

            else:
                reply = role.generate_response(role.vote_prompt(self.game_state))
                print(f"{role.name} 投票给 {reply}")
                votes[reply] = votes.get(reply, 0) + 1
                self.append_memory(f"{role.name} 投票给 {reply}")
        print("投票结果：")
        self.append_memory("投票结果：")
        for k, v in votes.items():
            print(f"{k}: {v} 票")
            self.append_memory(f"{k}: {v} 票")
        top_candidates = [r for r, v in votes.items() if v == max(votes.values())]
        top_candidates_list =[]
        for role in self.role_list:
            if role.name in top_candidates:
                top_candidates_list.append(role)

        if len(top_candidates) == 1:
            eliminated = top_candidates[0]
            self.game_state["死者"].append(eliminated)
            print(f"【投票结束】{eliminated} 被处决。")
            self.append_memory(f"【投票结束】{eliminated} 被处决。")
        
        # 平票二轮投票
        else:
            print(f"出现平票：{', '.join(top_candidates)}，将重新发言并二轮投票。")
            self.append_memory(f"出现平票：{', '.join(top_candidates)}，开始重新发言与二轮投票:")
            for role in top_candidates_list:
                if role.name == self.config.user_role:
                    user_input = input(f"请为自己辩护：")
                    self.append_memory(f"{role.name}的辩护：{user_input}")
                else:
                    reply = role.generate_response(role.again_prompt())
                    print(f"{role.name} 辩护：{reply}")
                    self.append_memory(f"{role.name}的辩护：{reply}")
            print("开始二轮投票：")
            votes2 = {}
            for role in alive_roles:
                if role.name in top_candidates:
                    continue
                if role.name == self.config.user_role:
                    vote = input(f"你是{self.config.user_role}，二轮投票请在以下候选中选择：{', '.join(top_candidates)}：")
                    votes2[vote] = votes2.get(vote, 0) + 1
                    self.append_memory(f"{role.name} 投票给 {vote}")
                else:
                    reply = role.generate_response(role.again_vote(top_candidates))
                    print(f"{role.name} 投票给 {reply}")
                    votes2[reply] = votes2.get(reply, 0) + 1
                self.append_memory(f"{role.name} 投票给 {reply}")
            print("二轮投票结果：")
            self.append_memory("二轮投票结果：")
            for k, v in votes2.items():
                print(f"{k}: {v} 票")
                self.append_memory(f"{k}: {v} 票")
            top_candidates = [r for r, v in votes2.items() if v == max(votes2.values())]
            top_candidates_list = []
            for role in alive_roles:
                if role.name in top_candidates:
                    top_candidates_list.append(role)
            if len(top_candidates) == 1:
                eliminated = top_candidates[0]
                self.game_state["死者"].append(eliminated)
                self.dead_list.append(top_candidates_list[0])
                print(f"【二轮投票结束】{eliminated} 被处决。")
                self.append_memory(f"【二轮投票结束】{eliminated} 被处决。")
            else:
                print("【二轮投票结束】无人出局，进入黑夜")
                self.append_memory(f"【二轮投票结束】无人出局，进入黑夜。")
    
    def append_memory(self,memory):
        for role in self.role_list:
            role.memory.append(memory)
