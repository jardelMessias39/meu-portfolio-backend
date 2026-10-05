import sys

with open('chat_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_rule = '9. IMPORTANTE: Antes de registrar um lead, agendar ou chamar a ferramenta de cria\xc3\xa7\xc3\xa3o de lead, exija e pergunte explicitamente pelo nome, e-mail, telefone e descri\xc3\xa7\xc3\xa3o do projeto/necessidade. N\xc3\xa3o invente nenhum desses dados para satisfazer os par\xc3\xa2metros da ferramenta.'
new_rule = '9. IMPORTANTE: Antes de registrar um lead ou agendar uma reuni\xc3\xa3o, exija e pergunte explicitamente pelos dados necess\xc3\xa1rios (nome, e-mail, telefone, empresa e necessidade/assunto). Para agendamento, exija tamb\xc3\xa9m a data e hor\xc3\xa1rio desejados. Confirme os dados antes de executar as ferramentas. N\xc3\xa3o invente nenhum desses dados para satisfazer os par\xc3\xa2metros.'

if old_rule not in content:
    print('Rule not found exactly. Searching...')
    lines = content.split('\\n')
    for i, line in enumerate(lines):
        if 'IMPORTANTE: Antes de registrar um lead' in line:
            lines[i] = new_rule
            content = '\\n'.join(lines)
            print('Replaced')
            break
else:
    content = content.replace(old_rule, new_rule)
    print('Replaced')

with open('chat_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
