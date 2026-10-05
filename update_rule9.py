import sys
import re

with open('chat_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'9\. IMPORTANTE: Antes de registrar um lead.*?satisfazer os par.metros da ferramenta\.', re.DOTALL)

new_rule = '''9. IMPORTANTE:
Para registrar um lead (create_lead), exija e pergunte explicitamente por: nome, e-mail, telefone, empresa e necessidade.
Para agendar uma reunião (schedule_meeting), exija e pergunte explicitamente por: nome, e-mail, telefone, empresa, data e horário desejados (formato ISO 8601), e assunto. Observações são opcionais.
Confirme os dados antes de executar as ferramentas. Não invente data ou horário, e não preencha dados falsos.'''

if pattern.search(content):
    content = pattern.sub(new_rule, content)
    with open('chat_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Rule replaced successfully.')
else:
    print('Rule not found.')
