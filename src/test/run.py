import os,sys,io
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')
sys.path.append(os.getcwd()+'/../../')

import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from functools import partial
import threading
import traceback

from src.config.config import Config
from src.env.env import *
from src.policy.policy import GameRule
from src.function.input import set_input_value

# 全局变量
config = Config()


# 主窗口
window = tk.Tk()
window.title("狼人杀互动创作助手")
window.geometry("800x600")


# NPC身份设置
identity_frame = tk.Frame(window)
identity_frame.pack(padx=10, pady=5, fill=tk.X)

role_labels = {}
identity = {}
role_objs = ["狼人", "村民", "预言家", "女巫"]

for x, player in enumerate(Config.role_names):   # 遍历role_names中的玩家名
    label = tk.Label(identity_frame, text=player, font=("宋体", 10))
    label.grid(row=0, column=x, padx=5)

    var = tk.StringVar()
    var.set(Config.role_identity[player])   
    identity_menu = ttk.Combobox(identity_frame, textvariable=var, values=role_objs, state="readonly", width=8)
    identity_menu.grid(row=1, column=x, padx=5)

    role_labels[player] = label
    identity[player] = var


# 聊天记录框
chat_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("宋体", 10))
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_box.tag_config("system", foreground="gray", justify="center", font=("宋体", 10))
chat_box.tag_config("bubble_left", background="#f0f0f0", justify="left", lmargin1=10, lmargin2=10, rmargin=60, spacing3=5)
chat_box.tag_config("bubble_right", background="#d2fdd2", justify="right", rmargin=10, lmargin1=60, lmargin2=60, spacing3=5)
chat_box.tag_config("name_left", font=("黑体", 9, "bold"), foreground="#555555", justify="left", lmargin1=10)
chat_box.tag_config("name_right", font=("黑体", 9, "bold"), foreground="#007700", justify="right", rmargin=10)



# 输入区域
input_frame = tk.Frame(window)
input_frame.pack(padx=10, pady=10, fill=tk.X)
input_text = tk.Text(input_frame, height=4, font=("宋体", 12), wrap=tk.WORD, bd=2, relief="groove")
input_text.grid(row=0, column=0, sticky="nsew", padx=(0, 10))


# 角色菜单
menu_frame = tk.Frame(input_frame, width=120) 
menu_frame.grid(row=0, column=1, sticky="nsew")

menu_label = tk.Label(menu_frame, text="角色菜单", font=("宋体", 10))
menu_label.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

selected_role = tk.StringVar()
selected_role.set("狼人")
role_menu = ttk.Combobox(menu_frame, textvariable=selected_role, values=role_objs, state="readonly", width=8)
role_menu.grid(row=1, column=0, sticky="nsew", pady=(0, 10))


# 布局
input_frame.grid_columnconfigure(0, weight=3)
input_frame.grid_columnconfigure(1, weight=1)  


# 初始化角色和游戏环境
def init_roles():
    config.role_identity = {config.user_role: selected_role.get(),**{name: var.get() for name, var in identity.items()}}
    for name in config.role_names:
        if config.role_identity.get(name) == "狼人":
            elsewolf_list=[] #狼队友列表
            for r in config.role_identity.keys():
                if config.role_identity.get(r) == "狼人" and r != name :
                    elsewolf_list.append(r)
            config.role_system_prompts[name] = f"你正在参与一场狼人杀游戏。你是{name}，请牢记自己的玩家序号。你的身份是狡猾而冷静的狼人，擅长伪装和引导。你的狼队友是{elsewolf_list}。" 
        if config.role_identity.get(name) == "村民":
            config.role_system_prompts[name] = f"你正在参与一场狼人杀游戏。你是{name}，请牢记自己的玩家序号。你的身份是普通村民，要认真分析局势帮助好人获胜。"
        if config.role_identity.get(name) == "预言家":
            config.role_system_prompts[name] = f"你正在参与一场狼人杀游戏。你是{name}，请牢记自己的玩家序号。你的身份是拥有查验能力的预言家，要带领好人识别狼人。"
        if config.role_identity.get(name) == "女巫":
            config.role_system_prompts[name] = f"你正在参与一场狼人杀游戏。你是{name}，请牢记自己的玩家序号。你的身份是谨慎的女巫，善于观察语言逻辑判断救毒时机。" 


# 将输出更改至聊天框
class StdoutRedirector(io.StringIO):
    def write(self, s):
        s = s.strip()
        if not s:
            return
        elif "：" in s and ">>>" not in s:
            name, content = s.split("：", 1)
            if name == "玩家1":
                chat_box.insert(tk.END, f"{name}：", "name_right")
                chat_box.insert(tk.END, f"{content}\n", "bubble_right")
            else:
                chat_box.insert(tk.END, f"{name}：", "name_left")
                chat_box.insert(tk.END, f"{content}\n", "bubble_left")
        else:
            chat_box.insert(tk.END, s + "\n", "system")
        chat_box.see(tk.END)
        super().write(s + "\n")

sys.stdout = StdoutRedirector()


def send():
    global user_input
    user_input = input_text.get("1.0", tk.END).strip()
    if user_input:
        print(f"{config.user_role}：{user_input}\n") 
        input_text.delete("1.0", tk.END)
        set_input_value(user_input)

send_button = tk.Button(menu_frame, text="发送", command=send)
send_button.grid(row=2, column=0, sticky="nsew")


#===============================================
'''                Game Start               '''   
#=============================================== 
print(f"你好，欢迎来到狼人杀互动创作空间，下面你将参与一场狼人杀游戏。\n"+f"你的用户名是{config.user_role}, 请为每位玩家分配身份。")
def run_game():
    day_idx = 1
    init_roles()
    env = BaseEnv(config=config,
                  count_s=0,
                  count_p=0)
    role_list = env.setup()
    game_rule = GameRule(config, env, role_list)
    while True:
        try:
            game_rule.night_kill()
            config.game_state["阶段"] = "白天"
            game_rule.play_round()
            game_rule.day_vote()
        except Exception as e:
            print(f"出错：{e}")
            traceback.print_exc()
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

def threaded_run_game():
    threading.Thread(target=run_game).start()

start_button = tk.Button(identity_frame, text="开始游戏", command=threaded_run_game)
start_button.grid(row=1,column=7, padx=5)


window.mainloop()