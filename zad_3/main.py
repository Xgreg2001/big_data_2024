import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma

# Definiujemy zakres wymiarów n
n = np.arange(1, 51)

# Definiujemy promienie
radii = [0.5, 1, 2]

# Obliczamy i zapisujemy wykresy dla każdego promienia r
for r in radii:
    Vn = (np.pi ** (n / 2) * r ** n) / gamma(n / 2 + 1)

    # Tworzymy nowy wykres dla każdego promienia
    plt.figure(figsize=(10, 6))
    plt.plot(n, Vn, marker='o', linestyle='-', color='b')

    # Dodajemy tytuł i etykiety osi
    plt.title(f'Objętość kuli o promieniu r = {r} w przestrzeni n-wymiarowej')
    plt.xlabel('Wymiar przestrzeni n')
    plt.ylabel('Objętość Vₙ(r)')
    plt.grid(True)

    # Zapisujemy wykres do pliku PDF
    plt.savefig(f'objętość_kuli_r_{r}.pdf')
    plt.close()
