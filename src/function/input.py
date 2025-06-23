import threading

input_event = threading.Event()
input_value = ""

# 从输入框input
def gui_input(prompt):
    global input_value
    print(prompt)             
    input_event.clear() 
    input_event.wait() # 阻塞，直到发送input
    return input_value

def set_input_value(value):
    global input_value
    input_value = value
    input_event.set()