import socket,threading
from LittlePiperDebugUtils.log import Logger
lg = Logger(Logger.INFO)

class Client():
    def __init__(self,host:str = '192.168.1.105', port:int = 21491):
        self.client_name = 'Default'
        self.socket_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket_client.connect((host, port))
        self.Running = True
        rt = threading.Thread(target=self.recvMessage,daemon=True)# 守护进程，主程序退出时也会退出
        rt.start()
        while True:
            msg = input(f"请输入客户端 {self.client_name} 发送给服务端 {host}:{port} 的数据：\n").strip()
            if msg == '': 
                lg.warning('关闭与服务器的连接')
                break
            try:
                self.socket_client.send(msg.encode("UTF-8"))
            except Exception as e:
                lg.error(e)
                break
        self.socket_client.close()
    def recvMessage(self):
        while self.Running:
            try:
                response = self.socket_client.recv(20480).decode("UTF-8")
                lg.success(f"收到服务端的消息：{response}")
            except Exception as e:
                lg.error(e)
    
 
if __name__ == '__main__':
    Client()