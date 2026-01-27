import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Substitua pela sua string com a senha real
# DICA: Se a senha tiver caracteres especiais, use letras/números ou codifique a URL
MONGO_URI = "mongodb+srv://jardelmessias28_db_user:<SUA_SENHA_AQUI>@jardel-db.cuaga3w.mongodb.net/?retryWrites=true&w=majority&appName=jardel-db"

def test_connection():
    print("Tentando conectar ao MongoDB Atlas...")
    try:
        # O timeout de 5 segundos evita que o script fique travado se o IP não estiver liberado
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # O comando ismaster é o jeito mais simples de forçar uma conexão e checar o status
        client.admin.command('ismaster')
        
        print("✅ CONEXÃO REALIZADA COM SUCESSO!")
        
        # Listar bancos para confirmar permissões
        dbs = client.list_database_names()
        print(f"Bancos de dados disponíveis: {dbs}")
        
    except OperationFailure as e:
        print(f"❌ ERRO DE AUTENTICAÇÃO: Verifique o usuário e a senha.\nDetalhes: {e}")
    except ConnectionFailure as e:
        print(f"❌ ERRO DE CONEXÃO: Verifique se o seu IP está liberado no Atlas (Network Access).\nDetalhes: {e}")
    except Exception as e:
        print(f"❌ OCORREU UM ERRO INESPERADO: {e}")

if __name__ == "__main__":
    test_connection()
    