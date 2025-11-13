# 🎮 Roguelike - Manual del Juego

## ¿Qué es este juego?
Es un **juego de aventuras por turnos** donde exploras mazmorras llenas de monstruos, tesoros y peligros. Cada vez que juegas, el mapa es diferente porque se genera aleatoriamente.

### ✨ Características principales:
- 🗺️ Mapas generados automáticamente
- ⚔️ Sistema de combate por turnos
- 🎯 Diferentes tipos de ataques
- 🏪 Tiendas para comprar objetos
- 📈 Sistema de niveles y experiencia
- 👻 Enemigos que se vuelven más fuertes
- ✨ Efectos visuales y partículas

---

## 🛠️ ¿Con qué está hecho?
- **Lenguaje**: Python 🐍
- **Biblioteca gráfica**: Pygame
- **No usa clases** - todo funciona con funciones y diccionarios

---

## 🎯 ¿Cómo funciona?
1. **Exploras** la mazmorra usando las flechas
2. **Encuentras** enemigos y entras en combate
3. **Derrotas** enemigos para ganar experiencia y oro
4. **Subes de nivel** para hacerte más fuerte
5. **Encuentras** la salida para pasar al siguiente nivel
6. **Compras** objetos en las tiendas

---

## 🎮 CONTROLES

### 🏃‍♂️ Movimiento:
- **↑** Mover arriba
- **↓** Mover abajo  
- **←** Mover izquierda
- **→** Mover derecha

### ⚔️ Ataques (en exploración):
- **A** - Disparar flecha (a distancia)
- **Z** - Ataque fuerte (cuerpo a cuerpo)

### 🏥 Utilidades:
- **P** - Beber poción de vida
- **S** - Entrar a la tienda (cuando estás sobre ella)
- **N** - Pasar al siguiente nivel (modo debug)

### ⚔️ Combate (cuando estás peleando):
- **1** - Ataque básico
- **2** - Defender (+6 defensa por 1 turno)
- **3** - Intentar huir
- **P** - Usar poción
- **A** - Disparar flecha
- **Z** - Golpe fuerte

### 🏪 Tienda:
- **1, 2, 3** - Comprar objetos
- **Q** - Salir de la tienda

---

## 👤 SISTEMA DE PERSONAJE

### Estadísticas del jugador:
- **HP**: Puntos de vida (si llegan a 0, mueres)
- **ATK**: Poder de ataque
- **DEF**: Defensa (reduce el daño recibido)
- **Nivel**: Tu nivel de experiencia
- **EXP**: Experiencia actual / Experiencia necesaria para subir
- **Oro**: Dinero para comprar en tiendas
- **Pociones**: Pociones de vida que puedes usar

### Subir de nivel:
Cuando llenas tu barra de experiencia, subes de nivel y ganas:
- **+HP** máximo
- **+ATK** (ataque)
- **+DEF** (defensa)

---

## 👹 ENEMIGOS

### Tipos de enemigos:
- **Nivel normal**: Igual que tu nivel
- **Nivel fuerte**: 1-2 niveles más que tú (30% de probabilidad)

### Comportamiento:
- **Patrullan** cuando no te ven
- **Te persiguen** cuando te detectan
- **Atacan** cuando están en tu casilla

---

## 🏪 TIENDA

### Objetos disponibles:
1. **Poción de Vida** (15 oro) - Recupera 25 HP
2. **Poción Grande** (25 oro) - Recupera 40 HP  
3. **Elixir de Fuerza** (35 oro) - +6 ATK por 8 turnos

---

## 🎨 ELEMENTOS VISUALES

### En el mapa:
- **⬛ Paredes** - No se puede pasar
- **⬜ Suelo** - Se puede caminar
- **🟦 Salida** - Te lleva al siguiente nivel
- **🟨 Tienda** - Para comprar objetos
- **🟩 Tú** - El jugador
- **🟥 Enemigos** - Criaturas que te atacan

### Efectos especiales:
- **✨ Partículas** - Cuando atacas o recibes daño
- **📝 Textos flotantes** - Muestran daño, experiencia, etc.
- **🌫️ Niebla de guerra** - Áreas no exploradas o fuera de visión

---

## 🔄 ESTADOS DEL JUEGO

- **🔍 Exploración** - Moviéndote por el mapa
- **⚔️ Combate** - Peleando con un enemigo  
- **🏪 Tienda** - Comprando objetos
- **💀 Game Over** - Cuando mueres

---