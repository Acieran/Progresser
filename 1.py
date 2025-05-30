import numpy as np
import matplotlib.pyplot as plt
import random

variant = 2
w = 4.68
step = 0.125
size = 330
t = 200
n = 80

# ПОДЗАДАЧА 1: Визуализация функций активации
x = np.arange(-w*2, w*2, step)

# Вычисление значений функций
sigmoid = 1 / (1 + np.exp(-x))
tanh = np.tanh(x)
relu = np.maximum(0, x)

# Первый вариант вывода: графики друг под другом
plt.figure(figsize=(10, 12))

# Сигмоида
plt.subplot(3, 1, 1)
plt.plot(x, sigmoid, color='blue', linestyle='-', label='Sigmoid')
plt.title(f'Вариант {variant}')
plt.xlabel('ФИО студента')
plt.ylabel('Группа')
plt.legend()

# Гиперболический тангенс (случайный цвет)
plt.subplot(3, 1, 2)
color_tanh = (random.random(), random.random(), random.random())
plt.plot(x, tanh, color=color_tanh, linestyle='-.', label='Tanh')
plt.title(f'Вариант {variant}')
plt.xlabel('ФИО студента')
plt.ylabel('Группа')
plt.legend()

# ReLU
plt.subplot(3, 1, 3)
plt.plot(x, relu, color='green', linestyle=':', label='ReLU')
plt.title(f'Вариант {variant}')
plt.xlabel('ФИО студента')
plt.ylabel('Группа')
plt.legend()

plt.tight_layout()
plt.show()