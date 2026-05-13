"""
金锤子 (GenForge) - MCP 服务器
Model Context Protocol - AI与CAD之间的通信桥梁
"""
import socket
import json
import threading
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP Server")


class MCPServer:
    def __init__(self, host='localhost', port=5678):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        
    def start(self):
        """启动 MCP 服务器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        logger.info(f"🔌 MCP 服务器已启动 ({self.host}:{self.port})")
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"📡 客户端连接: {address}")
                
                # 每个客户端一个线程
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                logger.error(f"接受连接错误: {e}")
                break
    
    def handle_client(self, client_socket, address):
        """处理客户端连接"""
        self.clients.append(client_socket)
        
        try:
            while self.running:
                # 接收数据
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # 解析命令
                try:
                    message = json.loads(data.decode('utf-8'))
                    response = self.process_command(message)
                    client_socket.send(json.dumps(response).encode('utf-8'))
                except json.JSONDecodeError:
                    error_response = {"status": "error", "message": "无效的JSON格式"}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    
        except Exception as e:
            logger.error(f"处理客户端错误: {e}")
        finally:
            client_socket.close()
            self.clients.remove(client_socket)
            logger.info(f"📴 客户端断开: {address}")
    
    def process_command(self, message):
        """处理命令"""
        command = message.get('command', '')
        
        if command == 'ping':
            return {"status": "ok", "message": "pong", "timestamp": time.time()}
        
        elif command == 'execute_code':
            # 执行 CAD/Revit 代码
            from MCP.code_executor import CodeExecutor
            executor = CodeExecutor()
            code = message.get('code', '')
            target = message.get('target', 'autocad')  # autocad 或 revit
            result = executor.execute(code, target)
            return result
        
        elif command == 'generate_model':
            # 生成模型
            from MCP.code_generator import ModelCodeGenerator
            generator = ModelCodeGenerator()
            params = message.get('params', {})
            target = message.get('target', 'autocad')
            code = generator.generate(params, target)
            return {"status": "ok", "code": code}
        
        elif command == 'get_status':
            # 获取状态
            return {
                "status": "ok",
                "server_status": "running",
                "clients_count": len(self.clients),
                "timestamp": time.time()
            }
        
        else:
            return {"status": "error", "message": f"未知命令: {command}"}
    
    def stop(self):
        """停止服务器"""
        self.running = False
        for client in self.clients:
            client.close()
        if self.server_socket:
            self.server_socket.close()
        logger.info("🛑 MCP 服务器已停止")


class MCPClient:
    """MCP 客户端 - 供 Agent 调用"""
    
    def __init__(self, host='localhost', port=5678):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """连接到 MCP 服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def send_command(self, command, params=None):
        """发送命令"""
        if not self.socket:
            if not self.connect():
                return {"status": "error", "message": "无法连接到MCP服务器"}
        
        message = {
            "command": command,
            **(params or {})
        }
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
            response = self.socket.recv(4096)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            logger.error(f"发送命令错误: {e}")
            return {"status": "error", "message": str(e)}
    
    def execute_code(self, code, target='autocad'):
        """执行代码"""
        return self.send_command('execute_code', {
            'code': code,
            'target': target
        })
    
    def generate_model(self, params, target='autocad'):
        """生成模型"""
        return self.send_command('generate_model', {
            'params': params,
            'target': target
        })
    
    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()


def start_server():
    """启动服务器"""
    server = MCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    start_server()
