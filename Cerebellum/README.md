# Cerebellum (atuador do Drone)
## API
> O código api.py é um servidor Flask que cria uma interface de controle do drone através de uma API REST. A API recebe comandos via POST da página web e atualiza o estado do drone de acordo com o comando recebido.

O servidor Flask é inicializado e o CORS é habilitado para permitir solicitações de diferentes origens. Em seguida, uma rota é definida para lidar com os comandos POST enviados para '/api/command'. A função handle_command é chamada quando uma solicitação POST é feita para essa rota.

A função handle_command primeiro verifica se os dados foram fornecidos na solicitação e se o comando está presente nos dados. Se não, ela retorna um erro. Em seguida, ela processa o comando e atualiza o estado do drone de acordo. Se o comando não for reconhecido, ela retorna um erro. Se o comando for processado com sucesso, ela retorna uma mensagem de sucesso.

A API pode tanto ser importada como um módulo em outro programa, como, se o script for executado diretamente, iniciado diretamente.


## Drone
> O código Drone.py é responsável por gerenciar um drone através de uma máquina de estados que, nas transições entre os estados realiza operações, e quando não há transição, segura os estadod e forma ativa. As operações se resumem a comandos enviados para o drone por meio de uma interface de comunicação serial.

O código Python é responsável por gerenciar um drone através de uma interface de comunicação serial. Ele é dividido em duas classes principais: DroneCommands e Drone.

A classe DroneCommands é responsável por conectar-se à placa do drone e enviar comandos para ela. A conexão é feita através da biblioteca MultiWii, que é uma biblioteca Python para comunicação com controladores de voo MultiWii. A classe DroneCommands tem métodos para iniciar e desligar o drone, além de métodos para enviar comandos de controle de voo para o drone.

A classe Drone representa o drone em si e lida com as transições de estado. O drone pode estar em um dos seguintes estados: IDLE, READY, KEEPING, RISING, FALLING, MOVING_RIGHT, MOVING_LEFT, SHUTTING_DOWN. Cada estado corresponde a um comportamento específico do drone, como subir, descer, mover-se para a direita ou esquerda, etc.

O método set_state da classe Drone é usado para alterar o estado do drone. Dependendo do estado, diferentes comandos são enviados para o drone. Por exemplo, se o estado for RISING, o drone é instruído a aumentar a potência do motor para subir. Se o estado for MOVING_RIGHT, o drone é instruído a mover-se para a direita.

O método keep_alive é usado para enviar continuamente comandos para o drone enquanto ele está em voo. Isso é necessário porque o drone precisa receber comandos constantemente para manter o voo estável.

O método gradual_update é usado para alterar gradualmente um parâmetro de controle de voo, como a potência do motor ou a direção do drone. Isso é feito enviando uma série de comandos que alteram o parâmetro de forma incremental.

Em resumo, este código Python é usado para controlar um drone através de uma interface de comunicação serial. Ele permite que o drone seja controlado de maneira precisa e responsiva, permitindo que ele execute uma variedade de manobras de voo.

## Telemetry
> O Telemetry.py é um software simples utilizado para fazer um teste nos sensores de telemetria da placa e conectividade solicitando dados relacionados a posição do drone.

O script começa importando o módulo MultiWii do pacote msp. Em seguida, tenta estabelecer uma conexão com a placa do drone através da porta serial "/dev/ttyACM0". Se a conexão for bem-sucedida, ele entra em um loop infinito onde coleta e imprime os dados de atitude e os canais RC do drone. Os dados de atitude incluem a orientação do drone (rotação em torno dos eixos x, y e z), enquanto os canais RC representam os comandos de controle remoto enviados ao drone (por exemplo, aceleração, rotação, etc.). Se ocorrer algum erro ao tentar estabelecer a conexão, ele imprime uma mensagem de erro e a exceção.

## MSP (multi serial protocol)
Este é um arquivo que possui uma versão alterada da biblioteca Multiwii Protocol. Ela utiliza a comunicação por MSP da controladora de voo e é utilizado pelo Raspberry Pi 4 Model B para enviar dados para a Controladora de Voo Mamba F405 MK2.

A controladora foi configurada utilizando o Betaflight configurator com o padrão de receiver AETR1234, que indica qual é a ordem que se deve enviar os valores durante um comando.

Como pode ser visto na classe do drone, utiliza-se o aetr1234(A, E, T, R), que depois utiliza o método de MSP sendCMD().

A função aetr simplifica a utilização de sendCMD, que existe um buffer completo. Este buffer é formado por 8 campos de 8 bits cada, cada um deles representando um dos valores de AETR1234.

