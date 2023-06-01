import time
import MultiWii

# Conecte-se à placa do drone
board = MultiWii("/dev/ttyACM0")

# Defina os valores iniciais para Aileron (A), Elevator (E), Throttle (T), Rudder (R)
A = 1500
E = 1500
T = 1010
R = 1500

# Defina os valores para os canais auxiliares
AUX1 = 1500
AUX2 = 1000
AUX3 = 1000
AUX4 = 1000

# Crie um loop para enviar comandos para o drone
while True:
    # Atualize os valores de A, E, T, R conforme necessário
    # Por exemplo, você pode aumentar o valor do acelerador (T) gradualmente
    if T < 1050:
        T += 1

    # Crie a mensagem para o drone
    message = [A, E, T, R, AUX1, AUX2, AUX3, AUX4]

    # Envie a mensagem para o drone
    board.sendCMD(8, MultiWii.SET_RAW_RC, message)

    # Aguarde um pouco antes de enviar a próxima mensagem
    time.sleep(0.02)  # 20ms delay
