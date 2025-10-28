import random
import math
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# --- Constantes do Gerador ---
NUM_ZONAS_DEMANDA = 12
NUM_LOCAIS_CANDIDATOS = 30
RAIO_DE_CONVENIENCIA = 50.0
SHOPPING_LARGURA = 300.0
SHOPPING_ALTURA = 200.0
MIN_DEMANDA = 10
MAX_DEMANDA = 40
MIN_CUSTO_FIXO = 1000
MAX_CUSTO_FIXO = 5000
MIN_CAPACIDADE = 30
MAX_CAPACIDADE = 60
# --- Fim das Constantes ---


def calcular_distancia(p1, p2):
    return math.dist(p1, p2)

def gerar_ponto_aleatorio(largura, altura):
    x = random.uniform(0, largura)
    y = random.uniform(0, altura)
    return (x, y)

def gerar_ponto_proximo(ponto_central, max_raio, largura, altura):
    r = random.uniform(0, max_raio)
    theta = random.uniform(0, 2 * math.pi)
    
    dx = r * math.cos(theta)
    dy = r * math.sin(theta)
    
    novo_x = max(0, min(largura, ponto_central[0] + dx))
    novo_y = max(0, min(altura, ponto_central[1] + dy))
    
    return (novo_x, novo_y)


def gerar_cenario():
    zonas_demanda = []
    locais_candidatos = []
    
    nomes_zonas = ["Praça de Alimentação", "Ala das Âncoras", "Área dos Cinemas", 
                   "Corredor Leste", "Corredor Oeste", "Entrada Principal", "Piso Superior",
                   "Área de Jogos", "Fraldário", "Lojas de Departamento"]
    random.shuffle(nomes_zonas)

    nomes_candidatos_possiveis = [
        "Perto da Entrada A", "Perto da Entrada B", "Corredor Central",
        "Perto dos Elevadores", "Perto da Escada Rolante N", "Perto da Escada Rolante S",
        "Ao lado do Banheiro 1", "Ao lado do Banheiro 2", "Corredor da C&A",
        "Em frente à Renner", "Lounge Piso 1", "Lounge Piso 2", 
        "Saída Estacionamento A1", "Saída Estacionamento B2", 
        "Balcão de Informações", "Perto da Lotérica", "Corredor de Serviços",
        "Ao lado da Starbucks", "Perto da Nike", "Entrada do Supermercado"
    ]
    
    nomes_necessarios = NUM_LOCAIS_CANDIDATOS
    nomes_disponiveis = len(nomes_candidatos_possiveis)
    if nomes_necessarios > nomes_disponiveis:
        for i in range(nomes_necessarios - nomes_disponiveis):
            nomes_candidatos_possiveis.append(f"Ponto Extra {i+1}")
            
    random.shuffle(nomes_candidatos_possiveis)

    
    for i in range(NUM_ZONAS_DEMANDA):
        nome = nomes_zonas.pop() if nomes_zonas else f"Zona Extra {i+1}"
        ponto = {
            "id": f"D{i+1}",
            "nome": nome,
            "localizacao": gerar_ponto_aleatorio(SHOPPING_LARGURA, SHOPPING_ALTURA),
            "demanda": random.randint(MIN_DEMANDA, MAX_DEMANDA)
        }
        zonas_demanda.append(ponto)
        
    
    for i in range(NUM_ZONAS_DEMANDA):
        ponto_demanda_central = zonas_demanda[i]["localizacao"]
        ponto = {
            "id": f"C{i+1}",
            "nome": nomes_candidatos_possiveis.pop(),
            "localizacao": gerar_ponto_proximo(ponto_demanda_central, 
                                               RAIO_DE_CONVENIENCIA, 
                                               SHOPPING_LARGURA, 
                                               SHOPPING_ALTURA),
            "custo_fixo": random.randint(MIN_CUSTO_FIXO, MAX_CUSTO_FIXO),
            "capacidade": random.randint(MIN_CAPACIDADE, MAX_CAPACIDADE)
        }
        locais_candidatos.append(ponto)
        
    
    num_restantes = NUM_LOCAIS_CANDIDATOS - NUM_ZONAS_DEMANDA
    for i in range(num_restantes):
        idx = NUM_ZONAS_DEMANDA + i + 1
        ponto = {
            "id": f"C{idx}",
            "nome": nomes_candidatos_possiveis.pop(),
            "localizacao": gerar_ponto_aleatorio(SHOPPING_LARGURA, SHOPPING_ALTURA),
            "custo_fixo": random.randint(MIN_CUSTO_FIXO, MAX_CUSTO_FIXO),
            "capacidade": random.randint(MIN_CAPACIDADE, MAX_CAPACIDADE)
        }
        locais_candidatos.append(ponto)
        
    random.shuffle(locais_candidatos)
    for idx, p in enumerate(locais_candidatos):
        p['id'] = f"C{idx+1}"
    
    return zonas_demanda, locais_candidatos


def salvar_em_csv(zonas_demanda, locais_candidatos):
    
    nome_arquivo_demanda = 'zonas_demanda.csv'
    headers_demanda = ['id', 'nome', 'localizacao_x', 'localizacao_y', 'demanda']
    
    with open(nome_arquivo_demanda, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_demanda)
        for p in zonas_demanda:
            loc_x = p['localizacao'][0]
            loc_y = p['localizacao'][1]
            writer.writerow([p['id'], p['nome'], f"{loc_x:.2f}", f"{loc_y:.2f}", p['demanda']])
            
    
    nome_arquivo_candidatos = 'locais_candidatos.csv'
    headers_candidatos = ['id', 'nome', 'localizacao_x', 'localizacao_y', 'custo_fixo', 'capacidade']
    
    with open(nome_arquivo_candidatos, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_candidatos)
        for p in locais_candidatos:
            loc_x = p['localizacao'][0]
            loc_y = p['localizacao'][1]
            writer.writerow([p['id'], p['nome'], f"{loc_x:.2f}", f"{loc_y:.2f}", p['custo_fixo'], p['capacidade']])


def plotar_cenario(zonas_demanda, locais_candidatos, raio_max, largura, altura):
    
    zd_x = [p['localizacao'][0] for p in zonas_demanda]
    zd_y = [p['localizacao'][1] for p in zonas_demanda]
    zd_labels = [f"{p['id']} ({p['demanda']})" for p in zonas_demanda]

    lc_x = [p['localizacao'][0] for p in locais_candidatos]
    lc_y = [p['localizacao'][1] for p in locais_candidatos]
    lc_labels = [p['id'] for p in locais_candidatos]

    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.scatter(lc_x, lc_y, c='blue', marker='o', s=50, label='Locais Candidatos (J)')
    for i, txt in enumerate(lc_labels):
        ax.annotate(txt, (lc_x[i], lc_y[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=9, color='darkblue')

    ax.scatter(zd_x, zd_y, c='red', marker='X', s=150, label='Zonas de Demanda (I)')
    for i, txt in enumerate(zd_labels):
        ax.annotate(txt, (zd_x[i], zd_y[i]), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9, color='darkred', weight='bold')

    for i, p in enumerate(zonas_demanda):
        label_raio = "Raio de Conveniência" if i == 0 else ""
        circulo = Circle(p['localizacao'], raio_max, color='red', fill=False, linestyle='--', alpha=0.6, label=label_raio)
        ax.add_patch(circulo)

    ax.set_title('Mapa do Cenário: Zonas de Demanda vs. Locais Candidatos', fontsize=16)
    ax.set_xlabel(f'Largura do Shopping (metros) - {largura}m')
    ax.set_ylabel(f'Altura do Shopping (metros) - {altura}m')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.7)
    
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    
    plt.tight_layout()
    
    # --- MODIFICAÇÃO PARA SALVAR O GRÁFICO DO CENÁRIO ---
    nome_arquivo_cenario = "cenario_inicial.png"
    plt.savefig(nome_arquivo_cenario, dpi=300, bbox_inches='tight')
    print(f"\nGráfico do cenário salvo em: {nome_arquivo_cenario}")
    # --- FIM DA MODIFICAÇÃO ---
    
    plt.show()


if __name__ == "__main__":
    
    zonas_demanda, locais_candidatos = gerar_cenario()
    
    salvar_em_csv(zonas_demanda, locais_candidatos)
    print("=" * 80)
    print("DADOS EXPORTADOS COM SUCESSO PARA:")
    print("- zonas_demanda.csv")
    print("- locais_candidatos.csv")
    print("=" * 80)
    
    
    print(f"\nPONTOS DE DEMANDA GERADOS (Total: {len(zonas_demanda)})")
    print("-" * 65)
    print(f"{'ID':<4} | {'Nome':<22} | {'Localização (X, Y)':<20} | Demanda")
    print("-" * 65)
    for p in zonas_demanda:
        loc_str = f"({p['localizacao'][0]:.1f}, {p['localizacao'][1]:.1f})"
        print(f"{p['id']:<4} | {p['nome']:<22} | {loc_str:<20} | {p['demanda']} usuários")
        
    print("\n" + "=" * 80)
    print(f"LOCAIS CANDIDATOS GERADOS (Total: {len(locais_candidatos)})")
    print("=" * 80)
    print(f"{'ID':<4} | {'Nome':<28} | {'Localização (X, Y)':<20} | Custo Fixo | Capacidade")
    print("-" * 80)
    for p in locais_candidatos:
        loc_str = f"({p['localizacao'][0]:.1f}, {p['localizacao'][1]:.1f})"
        print(f"{p['id']:<4} | {p['nome']:<28} | {loc_str:<20} | R$ {p['custo_fixo']:<6} | {p['capacidade']} portas")
        
        
    print("\n" + "=" * 80)
    print(f"VERIFICANDO RESTRIÇÃO (Raio de Conveniência = {RAIO_DE_CONVENIENCIA}m)")
    print("=" * 80)
    
    todas_atendidas = True
    for zd in zonas_demanda:
        coberta = False
        candidatos_proximos = []
        for lc in locais_candidatos:
            dist = calcular_distancia(zd["localizacao"], lc["localizacao"])
            if dist <= RAIO_DE_CONVENIENCIA:
                coberta = True
                candidatos_proximos.append(lc['id'])
        
        if coberta:
            print(f"[OK] Zona '{zd['nome']}' ({zd['id']}) está coberta por: {', '.join(candidatos_proximos)}")
        else:
            print(f"[FALHA] Zona '{zd['nome']}' ({zd['id']}) NÃO possui candidato próximo!")
            todas_atendidas = False
            
    print("-" * 80)
    if todas_atendidas:
        print("VERIFICAÇÃO CONCLUÍDA: Todos os pontos de demanda têm cobertura garantida.")
    else:
        print("ERRO NA GERAÇÃO: Nem todos os pontos foram cobertos.")
        
    
    print("\nExibindo o gráfico do cenário...")
    plotar_cenario(zonas_demanda, locais_candidatos, RAIO_DE_CONVENIENCIA, SHOPPING_LARGURA, SHOPPING_ALTURA)