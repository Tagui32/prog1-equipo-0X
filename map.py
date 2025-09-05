def generar_cuadrado(lado: int):
    matriz = []
    for i in range(lado):
        fila = []
        for j in range(lado):
            if i == 0 or i == lado - 1 or j == 0 or j == lado - 1:
                fila.append(1)
            else:
                fila.append(0)
        matriz.append(fila)
    return matriz