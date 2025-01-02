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
        self.delimiter = b'\n\n'
        self.buffer = []
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
                message = input().strip()
                if message.lower() == 'exit':
                    if self.Running:
                        lg.warning("关闭与服务器的连接喵")
                        self.socketClient.sendall(message.encode("UTF-8")+self.delimiter)
                        self.Running = False
                    break
                elif message.lower().startswith('_file '):
                    self.sendFile(message.split())
                    continue
                while True:
                    addition = input()
                    if not addition: break
                    message += '\n' + addition

                self.socketClient.sendall(message.encode("UTF-8")+self.delimiter)
            except (KeyboardInterrupt, EOFError):
                lg.warning("中断输入，准备关闭连接喵")
                self.Running = False
                break
            except Exception as e:
                lg.error(f"发送消息时发生错误喵: {e}")
                break
    def sendFile(self, cmd):
        if len(cmd) < 2:
            lg.error('需要提供文件路径喵.')
            return
        try:
            with open(cmd[1], 'rb') as f:
                data = f.read()
                self.socketClient.send(data+self.delimiter)
                lg.info(f'文件 {cmd[1]} 已发送喵.')
        except FileNotFoundError:
            lg.error(f'文件 {cmd[1]} 不存在喵.')
        except Exception as e:
            lg.error(f'文件发送时发生错误喵: {e}')
    # ---------------------------------------------------------------------------- #
    def recvMessage(self):
        while self.Running:
            try:
                self.recv(self.socketClient)
                if self.buffer and self.buffer[0].strip().lower() == 'shutdown':
                    lg.warning("服务端关闭了所有连接喵")
                    self.Running = False
                elif self.buffer:
                    self.show()
            except Exception as e:
                self.Running = False
                break
    def recv(self,conn:socket.socket)->bytes:
        while self.Running:
            chunk = conn.recv(1024)
            if not chunk: raise Exception('连接已关闭')
            self.buffer.append(chunk)
            if chunk.endswith(self.delimiter): break
    def show(self):
        lg.success(f"收到客户端的消息喵：{(b''.join([msg for msg in self.buffer]).decode().rstrip())}")
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
