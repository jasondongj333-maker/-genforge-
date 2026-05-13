"""
金锤子 (GenForge) - MCP 客户端
供 Agent 调用，向 MCP 服务器发送命令
"""
import socket
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP Client")


class MCPClient:
    """MCP 客户端 - 向 MCP 服务器发送命令"""
    
    def __init__(self, host='localhost', port=5678):
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = 30  # 超时时间（秒）
    
    def connect(self):
        """连接到 MCP 服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            logger.info(f"✅ 已连接到 MCP 服务器 ({self.host}:{self.port})")
            return True
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send_command(self, command, params=None):
        """发送命令"""
        if not self.socket:
            if not self.connect():
                return {"status": "error", "message": "无法连接到 MCP 服务器"}
        
        message = {
            "command": command,
            "timestamp": time.time(),
            **(params or {})
        }
        
        try:
            # 发送
            data = json.dumps(message).encode('utf-8')
            self.socket.sendall(data)
            
            # 接收响应
            response_data = self.socket.recv(8192)
            response = json.loads(response_data.decode('utf-8'))
            
            return response
            
        except socket.timeout:
            return {"status": "error", "message": "命令执行超时"}
        except Exception as e:
            logger.error(f"发送命令错误: {e}")
            return {"status": "error", "message": str(e)}
    
    def ping(self):
        """测试连接"""
        return self.send_command('ping')
    
    def execute_code(self, code, target='autocad'):
        """执行代码"""
        return self.send_command('execute_code', {
            'code': code,
            'target': target
        })
    
    def generate_model(self, intent, params, target='autocad'):
        """生成模型"""
        return self.send_command('generate_model', {
            'intent': intent,
            'params': params,
            'target': target
        })
    
    def get_status(self):
        """获取状态"""
        return self.send_command('get_status')


class CADExecutionManager:
    """CAD 执行管理器 - 封装代码执行流程"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.last_execution_result = None
    
    def execute_modeling(self, code, target='autocad'):
        """
        执行建模代码
        
        流程：
        1. 连接 MCP 服务器
        2. 发送代码
        3. 返回结果
        """
        logger.info(f"📤 开始执行建模代码 (目标: {target})")
        
        # 尝试连接并执行
        try:
            if not self.mcp_client.connect():
                # 服务器未运行，返回代码供手动执行
                logger.warning("⚠️ MCP 服务器未运行，返回代码供手动执行")
                return {
                    "status": "manual",
                    "message": "MCP 服务器未运行，请手动复制代码到 JZXZBOT 执行",
                    "code": code,
                    "target": target
                }
            
            result = self.mcp_client.execute_code(code, target)
            self.mcp_client.disconnect()
            
            self.last_execution_result = result
            return result
            
        except Exception as e:
            logger.error(f"执行失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "code": code,
                "target": target
            }
    
    def check_mcp_server(self):
        """检查 MCP 服务器状态"""
        try:
            if self.mcp_client.connect():
                result = self.mcp_client.ping()
                self.mcp_client.disconnect()
                return {"status": "running", "result": result}
            else:
                return {"status": "stopped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def execute_code_remotely(code, target='autocad'):
    """快捷函数：远程执行代码"""
    manager = CADExecutionManager()
    return manager.execute_modeling(code, target)


def check_server_status():
    """快捷函数：检查服务器状态"""
    manager = CADExecutionManager()
    return manager.check_mcp_server()
