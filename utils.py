import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import numpy as np

def contar_itens_lista(entradas, campo):
    """
    Conta itens em campos que podem ser strings separadas por vírgula
    ou listas
    """
    contagem = {}
    for entrada in entradas:
        lista = getattr(entrada, campo)
        if lista:
            if isinstance(lista, str):
                # Remove espaços e divide por vírgula
                itens = [item.strip() for item in lista.split(",") if item.strip()]
            else:
                itens = lista
            for item in itens:
                contagem[item] = contagem.get(item, 0) + 1
    return contagem

def gerar_grafico(contagem, titulo, xlabel, ylabel='Quantidade', small=False, nomes_abaixo=False):
    """
    Gera gráfico de barras a partir de um dicionário de contagem
    
    Args:
        contagem: dict com {categoria: valor}
        titulo: título do gráfico
        xlabel: label do eixo x
        ylabel: label do eixo y
        small: True para gráficos menores (dashboard)
        nomes_abaixo: True para colocar nomes abaixo das barras
    """
    if not contagem:
        # Retorna um gráfico vazio se não houver dados
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'Sem dados disponíveis', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=12, color='gray')
        ax.set_title(titulo, fontsize=11, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        imagem_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return imagem_base64
    
    categorias = list(contagem.keys())
    valores = list(contagem.values())

    # Ajuste do tamanho da figura
    if small:
        largura, altura = 5, 3.2
    else:
        largura = max(len(categorias) * 0.8, 6)
        altura = 6

    fig, ax = plt.subplots(figsize=(largura, altura))

    # Paleta de cores
    brand_colors = [
        '#556B2F', '#DAA520', '#8B4513', '#708090',
        '#6B8E23', '#FFD700', '#CD5C5C', '#4682B4',
        '#9ACD32', '#FF8C00', '#20B2AA', '#C71585', '#40E0D0'
    ]
    colors = [brand_colors[i % len(brand_colors)] for i in range(len(categorias))]

    barras = ax.bar(range(len(categorias)), valores, color=colors)

    ax.set_title(titulo, fontsize=11, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_xlabel(xlabel, fontsize=9)

    # Remove ticks do eixo X
    ax.set_xticks(range(len(categorias)))

    # Posicionamento dos nomes
    if nomes_abaixo:
        # nomes abaixo da barra (casos com poucas categorias)
        ax.set_xticklabels(categorias, rotation=0, fontsize=9, ha='center')
        # colocar valor acima da barra
        for barra, valor in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width()/2,
                valor + max(valores)*0.02,
                str(valor),
                ha='center', va='bottom',
                fontsize=8, fontweight='bold'
            )
    else:
        # nomes dentro da barra, vertical
        ax.set_xticklabels(['']*len(categorias))  # remove rótulos do eixo
        max_chars = 15  # limite de caracteres antes de colocar "..."
        for barra, nome, valor in zip(barras, categorias, valores):
            # truncar somente aqui
            if len(nome) > max_chars:
                nome = nome[:max_chars] + "..."
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width()/2,
                altura/2,
                f"{nome}\n({valor})",
                ha='center', va='center',
                rotation=90,
                fontsize=8, fontweight='bold', color='black'
            )

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=False)
    buf.seek(0)
    imagem_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return imagem_base64

def gerar_grafico_alta_resolucao(contagem, titulo, xlabel, ylabel='Quantidade', nomes_abaixo=False):
    """
    Versão em alta resolução para modais
    """
    if not contagem:
        # Retorna um gráfico vazio se não houver dados
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Sem dados disponíveis', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=16, color='gray')
        ax.set_title(titulo, fontsize=18, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        imagem_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return imagem_base64
    
    categorias = list(contagem.keys())
    valores = list(contagem.values())

    # Tamanho maior para alta resolução
    fig, ax = plt.subplots(figsize=(12, 8))

    # Paleta de cores
    brand_colors = [
        '#556B2F', '#DAA520', '#8B4513', '#708090',
        '#6B8E23', '#FFD700', '#CD5C5C', '#4682B4',
        '#9ACD32', '#FF8C00', '#20B2AA', '#C71585', '#40E0D0'
    ]
    colors = [brand_colors[i % len(brand_colors)] for i in range(len(categorias))]

    barras = ax.bar(range(len(categorias)), valores, color=colors)

    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xlabel(xlabel, fontsize=12)

    ax.set_xticks(range(len(categorias)))

    if nomes_abaixo:
        ax.set_xticklabels(categorias, rotation=45, fontsize=11, ha='right')
        for barra, valor in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width()/2,
                valor + max(valores)*0.01,
                str(valor),
                ha='center', va='bottom',
                fontsize=10, fontweight='bold'
            )
    else:
        ax.set_xticklabels(['']*len(categorias))
        max_chars = 20
        for barra, nome, valor in zip(barras, categorias, valores):
            if len(nome) > max_chars:
                nome = nome[:max_chars] + "..."
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width()/2,
                altura/2,
                f"{nome}\n({valor})",
                ha='center', va='center',
                rotation=90,
                fontsize=10, fontweight='bold', color='black'
            )

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', transparent=False)
    buf.seek(0)
    imagem_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return imagem_base64