import random
from openai import OpenAI
from collections import Counter
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 加载规则文档
def load_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path): #读取文件夹中的所有.txt文件
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r',encoding='utf-8') as file:
                documents.append(file.read()) #将文件内容读取为字符串添加到列表中
    return documents
rule = load_documents("./")

# 角色初始化
role_names=[f"玩家{i}"for i in range(2,8)]
role_messages = {role: [] for role in role_names}
role_memory = {role: [] for role in role_names}

# 用户角色
user_role="玩家1"

# 模型绑定
role_models={
    "玩家2": OpenAI(api_key="sk-c29297e3a3d2470a93d7833bbeacc96b", base_url="https://api.deepseek.com"),
    "玩家3": OpenAI(api_key="sk-8d94bdf8365844798f987bafd32ef2fc", base_url="https://api.deepseek.com"),
    "玩家4": OpenAI(api_key="sk-e5f37a9b2cea45069adbc7d603d4ad79", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
    "玩家5": OpenAI(api_key="sk-8cff54c6f47e4acfa7bb3ad4c3449918", base_url="https://api.deepseek.com"),
    "玩家6": OpenAI(api_key="sk-1e421593280e4733839b577c5de37d54", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
    "玩家7": OpenAI(api_key="sk-c29297e3a3d2470a93d7833bbeacc96b", base_url="https://api.deepseek.com"),
}

# 上帝视角身份信息
role_identity = {
    "玩家1": "狼人",
    "玩家2": "预言家",
    "玩家3": "女巫",
    "玩家4": "狼人",
    "玩家5": "村民",
    "玩家6": "村民",
    "玩家7": "村民",
}

# 初始提示词
role_system_prompts= {
    "玩家2": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家2，身份是拥有查验能力的预言家，要带领村民识别狼人。" ,
    "玩家3": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家3，身份是谨慎的女巫，善于观察语言逻辑判断救毒时机。",
    "玩家4": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家4，身份是狡猾而冷静的狼人，擅长伪装和引导。你的狼队友是玩家1。",
    "玩家5": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家5，身份是村民，紧张但希望帮助大家识破狼人。",
    "玩家6": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家6，身份是普通村民，推理不一定严谨，但会尽力思考。",
    "玩家7": f"你正在参与一场狼人杀游戏，请仔细查看规则{rule}。\n" + f"你是玩家7，身份是观察细致的村民，擅长发现逻辑漏洞。",
}

# 游戏状态
game_state={
    "阶段":"白天",
    "轮数":1,
    "死者": [],
    "发言顺序": random.sample([r for r in role_names] + [user_role], k=7)
}

# 夜晚狼人协商
def night_kill():
    wolves =  [r for r in role_names if role_identity.get(r) == "狼人" and r not in game_state["死者"]]
    if role_identity.get(user_role) == "狼人" and user_role not in game_state["死者"]:
        wolves += [user_role]
    wolf_log = []
    print("\n======= 狼人夜间密谋环节 =======")
    for w in role_names:
        if role_identity.get(w) == "狼人":
            role_memory[w].append(f"以下为你和狼队友夜间密谋的聊天记录:")
    for round_num in range(3):
        print(f"\n--- 第{round_num}轮协商 ---")
        for wolf in wolves:
            if wolf == user_role:
                user_input = input(f"你是{role_identity.get(user_role)}，请输入你的行动建议：")
                wolf_log.append(f"{user_role}：{user_input}")
                for w in role_names:
                    if role_identity.get(w) == "狼人":
                        role_memory[w].append(f"{user_role}：{user_input}")
            else:
                prompt = build_wolf_prompt(wolf)
                reply = generate_response(wolf, prompt)
                print(f"{wolf}：{reply}")
                wolf_log.append(f"{wolf}：{reply}")
                for w in role_names:
                    if role_identity.get(w) == "狼人":
                        role_memory[w].append(f"{wolf}：{reply}")
        
        # 每轮协商结果统计
        last_votes = {}
        for line in reversed(wolf_log):
            for wolf in wolves:
                if line.startswith(f"{wolf}：") and "我认为应该杀" in line:
                    if wolf not in last_votes:
                        target = line.split("我认为应该杀")[-1].strip().rstrip("。.!！")
                        last_votes[wolf] = target
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

    # 记录击杀
    game_state["死者"].append(target)
    print(f"[夜晚] 狼人杀死了：{target}\n")
    for w in role_names:
        if role_identity.get(w) == "狼人":
            role_memory[w].append(f"狼人密谋结束，你们决定杀{target}")
    for r in role_names:
        role_memory[w].append(f"天亮了，今天晚上死的是{target}")

   

# 狼人协商 prompt
def build_wolf_prompt(role):
    return (
        f"你是{role}，请和同伴协商今晚要杀谁。\n"
        f"这是之前所有人的全部聊天记录：\n" + "\n".join(role_memory[role]) +
        f"\n请你据此继续表达意见。请在发言最后明确写出“我认为应该杀玩家X”，其中X为序号。"
    )

# 白天角色发言prompt
def build_prompt(role):
    return(
        f"你是{role}，这是第{game_state['轮数']}天白天。\n"
        f"昨晚死亡角色：{', '.join(game_state['死者'])}。"
        f"这是之前所有人的全部聊天记录: \n" + "\n".join(role_memory[role]) + 
        "\n请你据此继续发言，说明你的判断、你怀疑或相信的人，或澄清自己的身份。"
    )

# 遗言prompt
def last_words(role):
    return(
        f"你是{role}，你昨天晚上死了。\n"
        f"这是之前所有人的全部聊天记录: \n" + "\n".join(role_memory[role]) + 
        "\n请你据此发表遗言，帮助你的阵营赢得游戏。"
    )

# 投票prompt
def vote_prompt(role):
    return(
        f"你是{role}，昨晚死亡角色：{', '.join(game_state['死者'])}。\n"
        f"这是之前所有人的全部行动记录: \n" + "\n".join(role_memory[role]) + 
        f"请投票决定活着的玩家中你最希望谁出局。请直接说出你要投票的玩家名(例如玩家1)，不要说任何其他内容。\n"
    )

# 二次辩护及投票
def again_prompt(role):
    return(
        f"你是{role}，目前投票中得票最多但出现平票"
        f"\n这是之前所有人的全部行动记录: \n" + "\n".join(role_memory[role]) + 
        f"请据此为自己辩护。\n"
    )

def again_vote(role, top_candidates):
    return(
        f"你是{role}，目前投票候选人：{', '.join(top_candidates)}。\n"
        f"这是之前所有人的全部行动记录: \n" + "\n".join(role_memory[role]) + 
        f"请据此投票决定候选人中你最希望谁出局。请直接说出你要投票的玩家名，不要说任何其他内容。\n"
    )


#生成回答
def generate_response(role, prompt):
    model = role_models[role]
    system =role_system_prompts.get(role)
    messages = [{"role": "system", "content": system}] + role_messages[role] + [{"role": "user", "content": prompt}]
    response = model.chat.completions.create(
        model = "deepseek-chat" if "deepseek" in str(model.base_url) else "qwen-plus",
        messages = messages,
        max_tokens=1024
    )
    reply = response.choices[0].message.content.strip()
    return reply


# 发言轮
def play_round():
    print(f"\n======= 第{game_state['轮数']}天 {game_state['阶段']} =======")
    for r in role_names:
            role_memory[r].append(f"天亮了，下面开始第{game_state['轮数']}天 {game_state['阶段']}的发言：")
    if game_state["轮数"] == 1:
        print(f"\n--- 死者发表遗言 ---")
        for r in role_names:
            role_memory[r].append(f"以下为死者发表遗言环节：")
        for role in game_state["死者"]:
            if role == user_role:
                user_input = input(f"您是{role}，昨天晚上您死了，请发表遗言")
                for r in role_names:
                    role_memory[r].append(f"{role}的遗言是：{user_input}")
            else:
                reply = generate_response(role, last_words(role))
                print(f"{role}：{reply}")
                for r in role_names:
                    role_memory[r].append(f"{role}的遗言是：{reply}")
        for r in role_names:
            role_memory[r].append(f"死者遗言发表结束，其余玩家开始发言:")

    for role in game_state["发言顺序"]:
        if role in game_state["死者"]:
            print(f"【{role}已死亡，跳过发言】")
            continue
        if role == user_role:
            user_input = input(f"你是{user_role}，请输入你的发言：")
            for r in role_names:
                role_memory[r].append(f"{role}：{user_input}")
        else:
            prompt = build_prompt(role)
            reply = generate_response(role, prompt)
            print(f"{role}：{reply}")
            for r in role_names:
                role_memory[r].append(f"{role}：{reply}")


    
# 投票环节
def day_vote():
    alive_roles = [r for r in role_names if r not in game_state["死者"]]
    if user_role not in game_state["死者"]:
        alive_roles += [user_role]
    print(f"\n======= 投票环节 =======")
    for r in role_names:
            role_memory[r].append(f"发言环节结束，现在开始投票")
    votes = {}
    for role in alive_roles:
        if role == user_role:
            vote = input(f"你是{user_role}，请输入你要投票的对象：")
            votes[vote] = votes.get(vote, 0) + 1
            for r in role_names:
                role_memory[r].append(f"{role} 投票给 {vote}")
        else:
            reply = generate_response(role, vote_prompt(role))
            print(f"{role} 投票给 {reply}")
            for r in role_names:
                role_memory[r].append(f"{role} 投票给 {reply}")
            votes[reply] = votes.get(r, 0) + 1
    print("投票结果：")
    for r in role_names:
        role_memory[r].append("投票结果：")
    for k, v in votes.items():
        print(f"{k}: {v} 票")
        for r in role_names:
            role_memory[r].append(f"{k}: {v} 票")
    top_candidates = [r for r, v in votes.items() if v == max(votes.values())]
    if len(top_candidates) == 1:
        eliminated = top_candidates[0]
        game_state["死者"].append(eliminated)
        print(f"【投票结束】{eliminated} 被处决。")
        for r in role_names:
            role_memory[r].append(f"【投票结束】{eliminated} 被处决。")
    
    # 平票二轮投票
    else:
        print(f"出现平票：{', '.join(top_candidates)}，将重新发言并二轮投票。")
        for r in role_names:
            role_memory[r].append(f"出现平票：{', '.join(top_candidates)}，开始重新发言与二轮投票:")
        for role in top_candidates:
            if role == user_role:
                user_input = input(f"请为自己辩护：")
                for r in role_names:
                    role_memory[r].append(f"{role}的辩护：{user_input}")
            else:
                reply = generate_response(role, again_prompt(role))
                print(f"{role} 辩护：{reply}")
                for r in role_names:
                    role_memory[r].append(f"{role}的辩护：{reply}")
        print("开始二轮投票：")
        votes2 = {}
        for role in alive_roles:
            if role in top_candidates:
                continue
            if role == user_role:
                vote = input(f"你是{user_role}，二轮投票请在以下候选中选择：{', '.join(top_candidates)}：")
                votes2[vote] = votes2.get(vote, 0) + 1
                for r in role_names:
                    role_memory[r].append(f"{role} 投票给 {vote}")
            else:
                reply = generate_response(role, again_vote(role, top_candidates))
                print(f"{role} 投票给 {reply}")
            for r in role_names:
                role_memory[r].append(f"{role} 投票给 {reply}")
            for r in alive_roles:
                if r in reply:
                    votes2[r] = votes2.get(r, 0) + 1
                break
        print("二轮投票结果：")
        for r in role_names:
            role_memory[r].append("二轮投票结果：")
        for k, v in votes2.items():
            print(f"{k}: {v} 票")
            for r in role_names:
                role_memory[r].append(f"{k}: {v} 票")
        top_candidates = [r for r, v in votes2.items() if v == max(votes2.values())]
        if len(top_candidates) == 1:
            eliminated = top_candidates[0]
            game_state["死者"].append(eliminated)
            print(f"【二轮投票结束】{eliminated} 被处决。")
            for r in role_names:
                role_memory[r].append(f"【二轮投票结束】{eliminated} 被处决。")
        else:
            print("【二轮投票结束】无人出局，进入黑夜")
            for r in role_names:
                role_memory[r].append(f"【二轮投票结束】无人出局，进入黑夜。")
                

#主函数
def main():
    print(f"你好，欢迎来到狼人杀互动创作空间，下面你将参与一场狼人杀游戏。\n"+f"你的用户名是{user_role}，身份为{role_identity.get(user_role)}。游戏开始。\n")
    night_kill()
    game_state["阶段"] = "白天"
    play_round()
    day_vote()
    
if __name__=="__main__":
    main()