from llm_provider import GeminiProvider, LLMResponse, GenericToolCall
import json
import uuid

class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MockPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call

class MockContent:
    def __init__(self, parts):
        self.parts = parts

class MockCandidate:
    def __init__(self, content):
        self.content = content

class MockResponse:
    def __init__(self, text=None, function_calls=None, candidates=None):
        self.text = text
        self.function_calls = function_calls
        self.candidates = candidates or []

response = MockResponse(
    candidates=[MockCandidate(content=MockContent(parts=[MockPart(function_call=MockFunctionCall(name="create_lead", args={"nome": "Teste"}))]))]
)

generic_tool_calls = None
text_content = None

if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
    parts = response.candidates[0].content.parts
    for p in parts:
        if p.function_call:
            if generic_tool_calls is None:
                generic_tool_calls = []
            
            fc_metadata = None
            if getattr(p, "thought_signature", None):
                import base64
                fc_metadata = {
                    "thought_signature": base64.b64encode(p.thought_signature).decode("utf-8")
                }
                
            fc_id = getattr(p.function_call, "id", None) or str(uuid.uuid4())
            
            generic_tool_calls.append(
                GenericToolCall(
                    id=fc_id,
                    name=p.function_call.name,
                    arguments=json.dumps(p.function_call.args) if p.function_call.args else "{}",
                    metadata=fc_metadata
                )
            )

print(generic_tool_calls)
