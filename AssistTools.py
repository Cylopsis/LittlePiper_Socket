import requests
import orjson as json
from LittlePiperDebugUtils import log as lg
class AssistTools:
    TOOL_CALL = 3
    def __init__(self):    
        self.addtionTools = dict()
        self.tool = [
            {
                "type": "function",
                "function": {
                    "name": "search_weather",
                    "description": "获取某个城市的天气信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "城市的adcode码"},
                            'extend':{'type':'string','description':'False 表示返回实况天气，True表示返回未来天气'},
                            "unit": {"type": "string", "enum": ["metric", "imperial"], "description": "温度单位"},
                        },
                        "required": ["city"],
                        "additionalProperties": False
                    }
                }
            }
        ]
    def run(self,funcName:str,funcArgs:dict,callID):
        match funcName:
            case 'search_weather':
                key = ''
                url = f'https://restapi.amap.com/v3/weather/weatherInfo'
                param = {
                    'city':funcArgs["city"],
                    'key':key,
                    'extensions':'all' if funcArgs['extend']=='True' else 'base'
                }
                weather = requests.get(url,params=param).json()
                message = {
                    "role": "tool",
                    "content":json.dumps(weather['forecasts' if funcArgs['extend']=='True' else 'lives'][0]).decode('utf-8'),
                    "tool_call_id": callID
                }
                return message
            case _:
                try:
                    runTool = self.addtionTools[funcName]
                except:
                    lg.error(lg.red('调用了不存在的工具函数'))
                    raise Exception('调用了不存在的工具函数')
                message = {
                    "role":"tool",
                    "content":json.dumps(runTool(funcArgs)).decode('utf-8'),
                    "tool_call_id":callID
                }
                return message
                
    def response_checker(self,response) -> int:
        match response.choices[0].finish_reason:
            case "length":
                lg.error("Error: The conversation was too long for the context window.")
                return 1
            case "content_filter":
                lg.error("Error: The content was filtered due to policy violations.")
                return 2       
            case "tool_calls":
                lg.info("Model made a tool call.")
                return AssistTools.TOOL_CALL
            case "stop":
                lg.warning("Model responded directly to the user.")
                return 4
            case _:
                lg.warning(f"Unexpected finish_reason: {response.choices[0].finish_reason}")
                return 5
ASSIST_TOOL = AssistTools()