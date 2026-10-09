import pytest
from models import ChatMessage, ChatSession
from pydantic import Field

def test_safe_history_slicing():
    # Helper to simulate the logic inside chat_service
    def simulate_slice(messages):
        MAX_HISTORY_MESSAGES = 20
        start_idx = max(0, len(messages) - MAX_HISTORY_MESSAGES)
        while start_idx > 0 and messages[start_idx].role == 'tool_result':
            start_idx -= 1
        return messages[start_idx:]

    # Scenario 1: Less than 20 messages -> No slicing
    messages = [ChatMessage(role="user", content=f"Msg {i}") for i in range(10)]
    sliced = simulate_slice(messages)
    assert len(sliced) == 10
    
    # Scenario 2: Exactly 20 messages -> No slicing effectively (start_idx = 0)
    messages = [ChatMessage(role="user", content=f"Msg {i}") for i in range(20)]
    sliced = simulate_slice(messages)
    assert len(sliced) == 20
    
    # Scenario 3: 25 messages, cutoff is at 5, which is a normal message -> simple slice
    messages = [ChatMessage(role="user", content=f"Msg {i}") for i in range(25)]
    sliced = simulate_slice(messages)
    assert len(sliced) == 20
    assert sliced[0].content == "Msg 5"
    
    # Scenario 4: 25 messages, cutoff at 5 is a tool_result. We must step back to 4 (assistant).
    # Indexes: 0..3 normal, 4: assistant, 5: tool_result, 6: tool_result, 7..24 normal.
    # Cutoff normally is len(25) - 20 = 5. At index 5, it's a tool_result!
    messages = []
    for i in range(25):
        if i == 4:
            messages.append(ChatMessage(role="assistant", content="calling tools"))
        elif i == 5 or i == 6:
            messages.append(ChatMessage(role="tool_result", content="result"))
        else:
            messages.append(ChatMessage(role="user", content=f"Msg {i}"))
            
    sliced = simulate_slice(messages)
    # The start_idx should shift back from 5 to 4.
    # We started with 25 messages. Normally start_idx = 5 (20 messages).
    # Since 5 is tool_result, it shifts to 4.
    # Slice from 4 to 24 means 21 messages.
    assert len(sliced) == 21
    assert sliced[0].role == "assistant"
    assert sliced[0].content == "calling tools"
    assert sliced[1].role == "tool_result"
    
    # Scenario 5: Multiple tool_results pushing the cutoff further back
    messages = []
    for i in range(25):
        if i == 2:
            messages.append(ChatMessage(role="assistant", content="calling tools 2"))
        elif i in [3, 4, 5, 6, 7]:
            messages.append(ChatMessage(role="tool_result", content="result"))
        else:
            messages.append(ChatMessage(role="user", content=f"Msg {i}"))
            
    # Cutoff normally is 5.
    # Index 5, 4, 3 are tool_results. So it should shift to 2 (assistant).
    sliced = simulate_slice(messages)
    assert len(sliced) == 23  # from 2 to 24
    assert sliced[0].role == "assistant"
    assert sliced[0].content == "calling tools 2"

