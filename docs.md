
## 实现方法
### 架构设计
- **游戏规则(GameRule)**：定义游戏规则，包括角色行动逻辑（如狼人杀人、预言家查验等）与多模型交互。
- **角色设计(Role)**：定义玩家特征，玩家名称、扮演角色、记忆等。
- **游戏配置(Config)**：定义游戏基本配置，如使用模型、玩家角色以及游戏基本背景等。
- **基本环境(BaseEnv)**：游戏角色配置初始化。
- **交互窗口设计**：使用***创建交互窗口 
  
- **系统流程图：**

```
用户选择玩家信息 → 智能体初始化 → 开始游戏 → 结果展示
```

#### 1. 角色设计与游戏配置
- **使用openai格式配置DeepSeek API：**
```python
role_models={
    "玩家2": OpenAI(api_key="sk-c29297e3a3d2470a93d7833bbeacc96b",
        base_url="https://api.deepseek.com")}
```
- **初始化：**
```python
class Role:
    def __init__(self, name:str, role:str, model):
        self.name = name # 玩家编号
        self.role = role # 玩家角色
        self.message = []
        self.model = model
        self.memory = [] # 玩家记忆
```
- **角色提示词设计:**
```python
def build_wolf_prompt(self):
```
```python
def build_prompt(self,game_state):
```
```python
def last_words(self):
```
- **调用API生成回答：**
```python
def generate_response(self, prompt):
    response = model.chat.completions.create(
        model = "deepseek-chat" if "deepseek" in str(model.base_url) else "qwen-plus",
        messages = messages,
        max_tokens=1024
    )
    reply = response.choices[0].message.content.strip()
    return reply
```
#### 2. 游戏规则
- **初始化：**
```python
def __init__(self,config:Config,env:BaseEnv,role_list:List[Role]):
```
##### 多智能体交互设计
在`GameRule`中，我们将狼人杀游戏分为：夜晚刀人、白天发言与投票环节。将对话内容放入每个角色的记忆当中，后使用合适的prompts生成回答以实现多智能体自动化交互功能。
```python
def night_kill(self):
    # 狼人间可进行多轮对话商议决定目标玩家
    # 预言家查验
    # 女巫可知当局的击杀目标并选择是否使用解药，同样也可选择是否使用毒药
```
```python
def play_round(self):
    # 当晚被击杀目标可先发表遗言
    # 随机打乱生成发言顺序，已死亡的玩家不能发言
```
```python
def day_vote(self):
    # 存活玩家根据发言内容进行顺序投票，投票最高者被放逐
    # 若一轮投票出现平票，将会举行二次投票
```