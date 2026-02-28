from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import aiohttp
import json

@register("mcbot_stress_test", "YourName", "基于 API 调用 mcbot 程序进行假人压测的插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://localhost:31545/api"

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 bot。注册成功后，发送 `/bot` 就会触发这个指令
    @filter.command("bot")
    async def bot(self, event: AstrMessageEvent):
        """mcbot 假人压测指令，仅管理员可用。使用方法：/bot start <服务器地址> <假人数量> 或 /bot stop"""
        # 检查是否为管理员
        if not event.is_admin():
            yield event.plain_result("权限不足，仅管理员可使用此指令")
            return

        message_str = event.message_str
        logger.info(f"Received message_str: '{message_str}'")
        args = message_str.split()
        logger.info(f"Parsed args: {args}")

        # 处理命令解析
        if len(args) < 1:
            yield event.plain_result("使用方法：/bot start <服务器地址> <假人数量> 或 /bot stop")
            return

        # 检查第一个参数是否是 'start' 或 'stop'
        if args[0] == "start":
            if len(args) < 3:
                yield event.plain_result("启动测试参数不足，使用方法：/bot start <服务器地址> <假人数量>")
                return

            server = args[1]
            count = args[2]
            # 设置默认值
            delay_min = args[3] if len(args) > 3 else "4000"
            delay_max = args[4] if len(args) > 4 else "5000"
            prefix = args[5] if len(args) > 5 else "ys_"

            await self.start_test(event, server, count, delay_min, delay_max, prefix)
        elif args[0] == "stop":
            await self.stop_test(event)
        else:
            yield event.plain_result("未知子指令，使用方法：/bot start <服务器地址> <假人数量> 或 /bot stop")

    async def start_test(self, event: AstrMessageEvent, server, count, delay_min, delay_max, prefix):
        """启动测试"""
        url = f"{self.api_url}/start_test"
        data = {
            "server": server,
            "count": count,
            "delay_min": delay_min,
            "delay_max": delay_max,
            "prefix": prefix,
            "plugin": "1.21.1.jar"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data)) as response:
                    result = await response.json()
                    yield event.plain_result(f"启动测试成功：{json.dumps(result, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"启动测试失败：{e}")
            yield event.plain_result(f"启动测试失败：{str(e)}")

    async def stop_test(self, event: AstrMessageEvent):
        """停止测试"""
        url = f"{self.api_url}/stop_test"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    result = await response.json()
                    yield event.plain_result(f"停止测试成功：{json.dumps(result, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"停止测试失败：{e}")
            yield event.plain_result(f"停止测试失败：{str(e)}")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
