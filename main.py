from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import aiohttp
import json

@register("plugin_upload_mcbot", "tniay", "基于 API 调用 mcbot 程序进行假人压测的插件，仅管理员可用", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://localhost:31545/api"

    async def initialize(self):
        """插件初始化方法"""
        logger.info("mcbot 假人压测插件初始化成功")

    @filter.command("bot")
    async def bot_command(self, event: AstrMessageEvent):
        """mcbot 假人压测指令
        
        使用方法：
        /bot start <服务器地址> <假人数量> [延迟最小值] [延迟最大值] [前缀]
        /bot stop
        
        示例：
        /bot start localhost:25565 10
        /bot stop
        """
        # 检查是否为管理员
        if not event.is_admin():
            yield event.plain_result("权限不足，仅管理员可使用此指令")
            return

        message_str = event.message_str
        logger.info(f"收到命令: '{message_str}'")
        args = message_str.split()
        logger.info(f"解析参数: {args}")

        # 处理命令解析
        if not args:
            yield event.plain_result("使用方法：/bot start <服务器地址> <假人数量> 或 /bot stop")
            return

        sub_command = args[0]
        
        if sub_command == "start":
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
        elif sub_command == "stop":
            await self.stop_test(event)
        else:
            yield event.plain_result("未知子指令，使用方法：/bot start <服务器地址> <假人数量> 或 /bot stop")

    async def start_test(self, event: AstrMessageEvent, server, count, delay_min, delay_max, prefix):
        """启动假人压测"""
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
                async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(data)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        yield event.plain_result(f"启动测试成功：{json.dumps(result, ensure_ascii=False)}")
                    else:
                        yield event.plain_result(f"启动测试失败：HTTP 状态码 {response.status}")
        except Exception as e:
            logger.error(f"启动测试失败：{e}")
            yield event.plain_result(f"启动测试失败：{str(e)}")

    async def stop_test(self, event: AstrMessageEvent):
        """停止假人压测"""
        url = f"{self.api_url}/stop_test"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        yield event.plain_result(f"停止测试成功：{json.dumps(result, ensure_ascii=False)}")
                    else:
                        yield event.plain_result(f"停止测试失败：HTTP 状态码 {response.status}")
        except Exception as e:
            logger.error(f"停止测试失败：{e}")
            yield event.plain_result(f"停止测试失败：{str(e)}")

    async def terminate(self):
        """插件销毁方法"""
        logger.info("mcbot 假人压测插件已销毁")
