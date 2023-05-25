# Sentinel Eyes

    Servidor C++ em um Raspberry Pi:
        Este servidor é responsável por obter os frames de uma câmera conectada ao Raspberry Pi.
        Depois de obter um frame, ele o envia para um cliente C++ que está sendo executado em um PC com arquitetura x86.

    Cliente C++ em um PC x86:
        Este cliente está recebendo os frames do servidor Raspberry Pi.
        Após receber um frame, ele o coloca em um arquivo FIFO (First In, First Out).
        O propósito do arquivo FIFO é servir como um buffer temporário para os frames, que estão sendo enviados para o servidor web.

    Servidor web em um PC x86:
        Este servidor web está lendo os frames do arquivo FIFO, que estão sendo escritos pelo cliente C++.
        Após ler um frame do arquivo FIFO, o servidor web o envia para uma página web React através de uma conexão WebSocket.

    Página web React em um PC x86 (client-side):
        Esta página web estabelece uma conexão WebSocket com o servidor web.
        Depois de estabelecer a conexão WebSocket, ela começa a receber os frames em tempo real que estão sendo enviados pelo servidor web.
        A página web React então exibe esses frames para o usuário final.