# Sentinel Eyes

    Servidor C++ em um Raspberry Pi:
        Este servidor é responsável por obter os frames de uma câmera conectada ao Raspberry Pi.
        Depois de obter um frame, ele o envia para um cliente C++ que está sendo executado em um PC com arquitetura x86.

    Cliente Python em um PC x86:
        Este cliente está recebendo os frames do servidor Raspberry Pi.
        Após receber um frame, ele o envia para o processamento de visão computacional.
        O processamento reconhece a face da pessoa e retorno um frame anotado com um bounding box e o nome.
        O resultado é mandado por websocket para o servidor web node.js.

    Servidor web em node.js em um PC x86:
        Este servidor web está lendo os frames do websocket, que estão sendo escritos pelo cliente Python.
        Após ler um frame, o servidor web o envia para uma página web React através de uma nova conexão WebSocket.

    Página web React em um PC x86 (client-side):
        Esta página web estabelece uma conexão WebSocket com o servidor web.
        Depois de estabelecer a conexão WebSocket, ela começa a receber os frames em tempo real que estão sendo enviados pelo servidor web.
        A página web React então exibe esses frames para o usuário final.