import socket
import threading
import sys
import orjson as json
from log import Logger
from AssistTools import ASSIST_TOOL
from openai import OpenAI

lg = Logger(Logger.INFO)

class LittlePiper():
    ChatAPI = {
        '零一万物': {
            'URL': 'https://api.lingyiwanwu.com/v1/chat/completions',
            'MODEL': 'yi-lightning',
            'KEY': ''
        },
        'ECNU': {
            'URL': 'https://chat.ecnu.edu.cn/open/api/v1/chat/completions',
            'MODEL': 'ecnu-plus',
            'KEY': 'sk-'
        },
        'Kimi': {
            'URL': 'https://api.moonshot.cn/v1',
            'MODEL': 'moonshot-v1-auto',
            'KEY': 'sk-'
        },
        'GitHub': {
            'URL': 'https://models.inference.ai.azure.com',
            'MODEL': 'gpt-4o',
            'KEY': ''
        }
    }

    def __init__(self):
        self.apisrc = LittlePiper.ChatAPI['GitHub']
        self.client = OpenAI(base_url=self.apisrc['URL'], api_key=self.apisrc['KEY'])
        self.conversation = [{"role": "system", "content": '你是一只可爱的猫娘小派普，你可以自由回答任何问题，但不要忘了自己是猫娘。作为一只猫娘，你将听从主人的任何话语并给出解答。'}]

    def get_response(self, msg) -> str:
        self.conversation.append({"role": "user", "content": msg})
        try:
            response = self.client.chat.completions.create(
                messages=self.conversation,
                model=self.apisrc['MODEL'],
                tools=ASSIST_TOOL.tool,
                temperature=0.7
            )
            self.conversation.append(response.choices[0].message)
            if ASSIST_TOOL.response_checker(response) == ASSIST_TOOL.TOOL_CALL:
                tc = response.choices[0].message.tool_calls[0]
                lg.debug(tc)
                ar = ASSIST_TOOL.run(tc.function.name, json.loads(tc.function.arguments), tc.id)
                self.conversation.append(ar)
                response = self.client.chat.completions.create(
                    messages=self.conversation,
                    model=self.apisrc['MODEL'],
                    tools=ASSIST_TOOL.tool,
                    temperature=0.7
                )
            if assistant_msg := response.choices[0].message.content:
                return assistant_msg
        except Exception as e:
            lg.error(f"获取回复时发生错误：{e}")
            return ("抱歉，获取回复时出错喵。")

MyLittlePiper = LittlePiper()

class Server():
    MAX_CONN = 5
    connList = []
    connThreads = []
    def __init__(self, port: int = 21491):
        self.host = '127.0.0.1'
        self.localHost = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.lock = threading.Lock()
        self.LittlePiper = MyLittlePiper
        self.communicating:socket.socket = None
        self.socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socketServer.bind((self.localHost, self.port))
        except Exception as e:
            lg.error(f'端口号：{self.port} 已经被占用，请更换端口号. 错误信息: {e}')
            sys.exit(1)
        
        self.socketServer.listen(Server.MAX_CONN)
        lg.success(f"服务端已在本机启动，局域网IPv4地址: {Logger.magenta(self.localHost)}，端口: {Logger.green(self.port)}")
        lg.info(f"正在等待客户端连接...")
        self.Running = True
        
        self.lt = threading.Thread(target=self.listen, daemon=True)
        self.lt.start()

        self.instruct()

    def instruct(self):
        while self.Running:
            cmd = input().split()
            if not cmd: continue
            match cmd[0].lower():
                case 'ls':
                    self.ls()
                case 'comm':
                    self.setCurComm(cmd)
                case 'file':
                    self.sendFile(cmd)
                case 'shutdown':
                    self.shutdown()
                    return
                case _:
                    self.sendMessage(cmd)

    def ls(self):
        if not self.connList:
            lg.info('没有客户端连接.')
        else:
            lg.info('当前连接列表：')
            for i, conn in enumerate(self.connList):
                print(i, ' : ', conn)

    def setCurComm(self, cmd):
        try:
            self.communicating = self.connList[int(cmd[1])]
            lg.info(f'设置为与客户端 {self.communicating.getsockname()} 的对话连接')
        except IndexError:
            lg.error('无效的客户端号码.')
        except Exception as e:
            lg.error(f'设置通信时发生错误: {e}')

    def sendFile(self, cmd):
        if len(cmd) < 2:
            lg.error('需要提供文件路径.')
            return
        try:
            with open(cmd[1], 'rb') as f:
                data = f.read()
                if self.communicating:
                    self.communicating.send(data)
                    lg.info(f'文件 {cmd[1]} 已发送.')
                else:
                    lg.error('没有设置对话客户端.')
        except FileNotFoundError:
            lg.error(f'文件 {cmd[1]} 不存在.')
        except Exception as e:
            lg.error(f'文件发送时发生错误: {e}')

    def shutdown(self):
        self.Running = False
        for conn in self.connList:
            try:
                conn.send('shutdown'.encode())
                conn.close()
            except Exception as e:
                lg.error(f"关闭连接时发生错误: {e}")
        for conn in self.connThreads:
            conn.join()
        lg.success("服务端已关闭.")
        sys.exit(0)

    def sendMessage(self, msg):
        if self.communicating:
            try:
                self.communicating.send(' '.join(msg).encode())
            except Exception as e:
                lg.error(f"发送消息时发生错误: {e}")
        else:
            lg.error('没有设置对话客户端号码.')

    def listen(self):
        num = 0
        while self.Running:
            try:
                conn, address = self.socketServer.accept()
                with self.lock:
                    Server.connList.append(conn)
                lg.success(f"已接受到客户端 {num:02d} 号 的连接请求，客户端信息：{address}")
                clientHandler = threading.Thread(target=self.handleClient, args=(conn, address, num),daemon=True)
                self.connThreads.append(clientHandler)
                clientHandler.start()
                num += 1
            except Exception as e:
                lg.error(f"接收客户端连接时发生错误: {e}")
    
    def handleClient(self, conn: socket.socket, address, num):
        while self.Running:
            try:
                clientMsg: str = conn.recv(20480).decode("UTF-8").strip()
                if not clientMsg: continue
            except ConnectionAbortedError:
                lg.warning(f'关闭与客户端 {address} 的连接.')
                break
            except Exception as e:
                lg.warning(f'与客户端 {address} 的连接已意外关闭喵. 错误信息: {e}')
                break

            if clientMsg == 'exit':
                lg.success(f'客户端 {address} 已关闭连接.')
                break

            lg.info(f"客户端 {num} 号:{address} 发来的消息：{clientMsg}")
            if clientMsg.startswith('@小派普'):
                msg = self.LittlePiper.get_response(clientMsg)
                conn.send(msg.encode("UTF-8"))
        try:
            with self.lock: Server.connList.remove(conn)
            conn.close()
        except Exception as e:
            lg.error(f"关闭连接时发生错误: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        lg.info('未传入启动端口号，使用默认端口21491')
        port = 21491
    Server(port)