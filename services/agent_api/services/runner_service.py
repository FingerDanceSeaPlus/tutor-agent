import asyncio
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RunnerService:
    """Runner服务"""
    def __init__(self):
        self.timeout = 5  # 执行超时时间（秒）

    async def run_code(self, code: str, language: str, input_data: str = "") -> Dict[str, Any]:
        """运行代码"""
        if language == "python":
            return await self._run_python(code, input_data)
        elif language == "javascript":
            return await self._run_javascript(code, input_data)
        else:
            return {
                "ok": False,
                "output": "",
                "error": f"不支持的语言: {language}",
                "execution_time": None
            }

    async def _run_python(self, code: str, input_data: str) -> Dict[str, Any]:
        """运行Python代码"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 运行代码
            process = await asyncio.create_subprocess_exec(
                "python", temp_file,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 输入数据
            stdin_data = input_data.encode() if input_data else b""

            # 执行代码
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=stdin_data),
                timeout=self.timeout
            )

            # 解码输出
            output = stdout.decode('utf-8')
            error = stderr.decode('utf-8') if stderr else None

            # 检查执行是否成功
            ok = process.returncode == 0

            return {
                "ok": ok,
                "output": output,
                "error": error,
                "execution_time": None  # 暂时不计算执行时间
            }
        except asyncio.TimeoutError:
            process.kill()
            return {
                "ok": False,
                "output": "",
                "error": "执行超时",
                "execution_time": None
            }
        except Exception as e:
            logger.error(f"运行Python代码失败: {e}")
            return {
                "ok": False,
                "output": "",
                "error": str(e),
                "execution_time": None
            }
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    async def _run_javascript(self, code: str, input_data: str) -> Dict[str, Any]:
        """运行JavaScript代码"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 运行代码
            process = await asyncio.create_subprocess_exec(
                "node", temp_file,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 输入数据
            stdin_data = input_data.encode() if input_data else b""

            # 执行代码
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=stdin_data),
                timeout=self.timeout
            )

            # 解码输出
            output = stdout.decode('utf-8')
            error = stderr.decode('utf-8') if stderr else None

            # 检查执行是否成功
            ok = process.returncode == 0

            return {
                "ok": ok,
                "output": output,
                "error": error,
                "execution_time": None  # 暂时不计算执行时间
            }
        except asyncio.TimeoutError:
            process.kill()
            return {
                "ok": False,
                "output": "",
                "error": "执行超时",
                "execution_time": None
            }
        except Exception as e:
            logger.error(f"运行JavaScript代码失败: {e}")
            return {
                "ok": False,
                "output": "",
                "error": str(e),
                "execution_time": None
            }
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
