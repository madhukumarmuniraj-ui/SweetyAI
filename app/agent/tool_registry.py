class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(self, name, description, function, parameters):
        self.tools[name] = {
            "function": function,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            },
        }

    def get(self, name):
        return self.tools.get(name)

    def get_schemas(self):
        return [
            tool["schema"]
            for tool in self.tools.values()
        ]

    def execute(self, name, arguments):
        tool = self.get(name)

        if tool is None:
            return f"Unknown tool: {name}"

        try:
            return str(
                tool["function"](**arguments)
            )
        except Exception as e:
            return f"Tool error: {e}"

    def list_tools(self):
        return list(self.tools.keys())
