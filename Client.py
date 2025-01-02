import socket
import threading
import sys
from log import Logger

lg = Logger(Logger.INFO)

class Client:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 21491, name: str = 'Default'):
        self.name = name
        self.host = host
        self.port = port
        self.Running = True
        # ------------------------------------------------------------------------ #
        try:
            self.socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socketClient.connect((self.host, self.port))
            lg.info(f"客户端 {self.name} 已连接到服务端 {self.host}:{self.port}喵")
        except Exception as e:
            lg.error(f"无法连接到服务器 {self.host}:{self.port} 喵 - {e}")
            sys.exit(1)
        # ------------------------------------------------------------------------ #
        self.rt = threading.Thread(target=self.recvMessage, daemon=True)
        self.rt.start()
        # ------------------------------------------------------------------------ #
        self.sendMessage()
        # ------------------------------------------------------------------------ #
        self.shutdown()
    # ---------------------------------------------------------------------------- #
    def sendMessage(self):
        lg.info("请输入消息（输入exit退出，两次回车表示输入消息结束）：")
        while self.Running:
            try:
                message = input()
                if message.strip().lower() == 'exit':
                    if self.Running:
                        lg.warning("关闭与服务器的连接喵")
                        self.socketClient.sendall(message.encode("UTF-8"))
                        self.Running = False
                    break
                elif message.strip().lower().startswith('_file '):
                    filename = message.strip()[6:].strip()
                    self.sendMessageFromFile(filename)
                    continue
                else:
                    while True:
                        addition = input().strip()
                        if not addition: break
                        message += '\n' + addition

                    self.socketClient.sendall(message.encode("UTF-8"))
            except (KeyboardInterrupt, EOFError):
                lg.warning("中断输入，准备关闭连接喵")
                self.Running = False
                break
            except Exception as e:
                lg.error(f"发送消息时发生错误喵: {e}")
                break
    # ---------------------------------------------------------------------------- #
    def recvMessage(self):
        while self.Running:
            try:
                response = self.socketClient.recv(20480).decode("UTF-8")
                if response and response.strip().lower() == 'shutdown':
                    lg.warning("服务端关闭了所有连接喵")
                    self.Running = False
                elif response:
                    lg.success(f"收到服务端的消息喵：{response}")
            except Exception as e:
                self.Running = False
                break
    # ---------------------------------------------------------------------------- #
    def sendMessageFromFile(self, filename: str):
        try:
            with open(filename, 'rb') as file:
                message = file.read().strip()
                if message:
                    self.socketClient.sendall(message)
                else:
                    lg.warning(f"文件 {filename} 是空的喵")
        except FileNotFoundError:
            lg.error(f"文件 {filename} 未找到喵")
        except Exception as e:
            lg.error(f"读取文件 {filename} 时发生错误喵: {e}")
    # ---------------------------------------------------------------------------- #
    def shutdown(self):
        try:
            self.socketClient.close()
            lg.success("客户端已关闭喵")
            sys.exit(0)
        except Exception as e:
            lg.error(f"关闭客户端时发生错误喵: {e}")
# -------------------------------------------------------------------------------- #
if __name__ == '__main__':
    if len(sys.argv) == 3:
        try:
            host = sys.argv[1]
            port = int(sys.argv[2])
            Client(host, port)
        except ValueError:
            lg.error("端口号必须是整数喵")
            sys.exit(1)
        except Exception as e:
            lg.error(f"启动客户端时发生错误喵: {e}")
            sys.exit(1)
    else:
        lg.warning("用法: python client.py <服务端IP> <服务端端口号>喵")
        sys.exit(1)