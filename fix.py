with open('tools_executor.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\\n        self.create_lead_schema', '        self.create_lead_schema')
content = content.replace('\\n        return json.dumps', '        return json.dumps')

with open('tools_executor.py', 'w', encoding='utf-8') as f:
    f.write(content)
