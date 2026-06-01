
def optional_import(name):
    try:
        return __import__(name)
    except ImportError:
        return None
    
# TODO: Refatorar para usar um sistema de importação opcional mais robusto, que permita lidar com dependências opcionais de forma mais elegante e informativa. O código atual é um exemplo simples de função de importação opcional, mas a ideia é criar uma estrutura que possa fornecer mensagens de erro mais claras ou alternativas quando uma dependência não estiver disponível.