"""Tabelas das armas: espadas (corpo a corpo) e sub-armas (arremesso, gastam corações)."""

ESPADAS = [
    dict(nome="Espada de Ferro", dano=2, alcance=74, prep=0.07, golpe=0.09, recup=0.13, cor=(255, 255, 255, 255),
         icone=11, empurrao=4, som="golpe"),
    dict(nome="Lâmina Veloz", dano=2, alcance=68, prep=0.04, golpe=0.07, recup=0.07, cor=(150, 255, 190, 255),
         icone=12, empurrao=3, som="golpe_leve"),
    dict(nome="Sabre do Sol", dano=5, alcance=96, prep=0.11, golpe=0.11, recup=0.20, cor=(255, 190, 90, 255),
         icone=13, empurrao=8, som="golpe_pesado"),
    dict(nome="Presa Rubra", dano=4, alcance=86, prep=0.08, golpe=0.10, recup=0.15, cor=(255, 90, 100, 255),
         icone=14, empurrao=6, som="golpe_pesado"),
]

SUBARMAS = {
    "adaga": dict(nome="Adaga", custo=1, icone=7, dano=2),
    "machado": dict(nome="Machado", custo=2, icone=8, dano=4),
    "agua": dict(nome="Água Benta", custo=2, icone=9, dano=2),
    "bumerangue": dict(nome="Bumerangue", custo=2, icone=10, dano=3),
}
