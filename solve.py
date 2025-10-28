import pandas as pd
import pulp
import math
import matplotlib.pyplot as plt

def calcular_distancia(ponto1, ponto2):
    """Calcula a distância Euclidiana entre dois pontos (x, y)."""
    return math.sqrt((ponto1[0] - ponto2[0])**2 + (ponto1[1] - ponto2[1])**2)

def resolver_localizacao_estacoes():
    """
    Resolve o problema de otimização de localização de estações de recarga
    com base nos arquivos CSV fornecidos e no modelo matemático.
    """
    
    # --- 1. Carregar Dados ---
    try:
        df_demanda = pd.read_csv("zonas_demanda.csv")
        df_candidatos = pd.read_csv("locais_candidatos.csv")
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado. Verifique o nome/caminho do arquivo: {e.filename}")
        return

    # --- 2. Definir Conjuntos e Índices ---
    I = df_demanda['id'].tolist()  # Conjunto de pontos de demanda
    J = df_candidatos['id'].tolist() # Conjunto de pontos candidatos

    # --- 3. Preparar Parâmetros ---
    
    # Copiamos os dados para a plotagem
    plot_df_demanda = df_demanda.copy()
    plot_df_candidatos = df_candidatos.copy()

    df_demanda.set_index('id', inplace=True)
    df_candidatos.set_index('id', inplace=True)

    # d_i: Demanda do ponto i
    d = df_demanda['demanda'].to_dict()
    
    # c_j: Custo fixo da instalação j
    c = df_candidatos['custo_fixo'].to_dict()
    
    # K_j: Capacidade da instalação j
    K = df_candidatos['capacidade'].to_dict()

    # Coordenadas para cálculo da distância
    loc_demanda = df_demanda.apply(lambda row: (row['localizacao_x'], row['localizacao_y']), axis=1).to_dict()
    loc_candidatos = df_candidatos.apply(lambda row: (row['localizacao_x'], row['localizacao_y']), axis=1).to_dict()

    # a_ij: Parâmetro binário de conveniência (distância <= 50)
    a = {}
    for i in I:
        for j in J:
            dist = calcular_distancia(loc_demanda[i], loc_candidatos[j])
            a[(i, j)] = 1 if dist <= 50 else 0

    # --- 4. Modelagem Matemática com PuLP ---
    
    prob = pulp.LpProblem("Problema_Localizacao_Estacoes", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", J, cat=pulp.LpBinary)
    prob += pulp.lpSum(c[j] * x[j] for j in J), "Custo_Total"

    # --- 5. Adicionar Restrições ---
    
    for i in I:
        # Restrição de Conveniência (Cobertura Mínima):
        prob += pulp.lpSum(a[(i, j)] * x[j] for j in J) >= 1, f"Cobertura_Minima_{i}"
        
        # Restrição de Atendimento de Demanda (Capacidade):
        prob += pulp.lpSum(a[(i, j)] * K[j] * x[j] for j in J) >= d[i], f"Atendimento_Demanda_{i}"

    # --- 6. Resolver o Problema ---
    
    print("Iniciando a resolução do problema...")
    prob.solve()

    # --- 7. Exibir Resultados ---
    
    print("="*30)
    print(f"Status da Solução: {pulp.LpStatus[prob.status]}")
    print("="*30)

    if pulp.LpStatus[prob.status] == 'Optimal':
        print(f"Custo Total Mínimo: {pulp.value(prob.objective):.2f}")
        print("\nEstações a serem instaladas (xj = 1):")
        
        ids_instalados = []
        for j in J:
            if x[j].varValue == 1:
                nome_local = df_candidatos.loc[j, 'nome']
                print(f"  - {j}: {nome_local}")
                ids_instalados.append(j)

        # --- 8. PLOTAR GRÁFICO (NOVA SEÇÃO) ---
        
        print("\nGerando gráfico da solução...")

        # Separar os locais candidatos em "instalados" e "não instalados"
        df_instalados = plot_df_candidatos[plot_df_candidatos['id'].isin(ids_instalados)]
        df_nao_instalados = plot_df_candidatos[~plot_df_candidatos['id'].isin(ids_instalados)]

        fig, ax = plt.subplots(figsize=(14, 10))

        # 1. Plotar Pontos de Demanda (I)
        ax.scatter(
            plot_df_demanda['localizacao_x'], 
            plot_df_demanda['localizacao_y'],
            c='blue', 
            marker='o', 
            s=80, # Tamanho maior
            label='Pontos de Demanda (I)'
        )
        # Adicionar rótulos (IDs) aos pontos de demanda
        for _, row in plot_df_demanda.iterrows():
            ax.annotate(row['id'], (row['localizacao_x'], row['localizacao_y']), 
                        textcoords="offset points", xytext=(5,5), ha='center', color='darkblue')

        # 2. Plotar Candidatos Não Instalados (J)
        ax.scatter(
            df_nao_instalados['localizacao_x'], 
            df_nao_instalados['localizacao_y'],
            c='gray', 
            marker='s', # 's' = square (quadrado)
            s=30,
            label='Candidatos Não Instalados',
            alpha=0.7
        )

        # 3. Plotar Estações Instaladas (x_j = 1)
        ax.scatter(
            df_instalados['localizacao_x'], 
            df_instalados['localizacao_y'],
            c='green', 
            marker='s', 
            s=100, # Tamanho maior
            edgecolor='black',
            label='Estações Instaladas (x_j = 1)'
        )
        # Adicionar rótulos (IDs) às estações instaladas
        for _, row in df_instalados.iterrows():
            ax.annotate(row['id'], (row['localizacao_x'], row['localizacao_y']), 
                        textcoords="offset points", xytext=(5,5), ha='center', color='darkgreen', weight='bold')
            
            # Adicionar o círculo de conveniência (raio de 50)
            circle = plt.Circle((row['localizacao_x'], row['localizacao_y']), 
                                50, color='green', fill=False, linestyle='--', alpha=0.6)
            ax.add_patch(circle)

        
        # Configurações do Gráfico
        ax.set_title("Solução Ótima: Localização de Estações de Recarga")
        ax.set_xlabel("Localização X")
        ax.set_ylabel("Localização Y")
        ax.legend(loc='upper right') # Sua modificação mantida
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_aspect('equal', adjustable='box') # Garante que o raio de 50m seja um círculo
        
        # Ajusta o layout (removido o 'rect' que não é mais necessário)
        plt.tight_layout() 
        
        # --- MODIFICAÇÃO PARA SALVAR O ARQUIVO ---
        nome_arquivo_saida = "resultado_localizacao.png"
        # Salva a figura antes de mostrá-la
        # dpi=300 aumenta a resolução da imagem
        # bbox_inches='tight' garante que a legenda e os rótulos não sejam cortados
        plt.savefig(nome_arquivo_saida, dpi=300, bbox_inches='tight')
        print(f"\nGráfico salvo com sucesso em: {nome_arquivo_saida}")
        # --- FIM DA MODIFICAÇÃO ---

        plt.show() # Mostra o gráfico na tela

            
    elif pulp.LpStatus[prob.status] == 'Infeasible':
        print("O problema é inviável.")
        print("Isso significa que não há solução que satisfaça todas as restrições.")
        print("Possíveis causas:")
        print("  - Algum ponto de demanda (i) não pode ser coberto por nenhuma estação (a_ij = 0 para todo j).")
        print("  - A capacidade das estações convenientes não é suficiente para atender a demanda (d_i).")
    else:
        print("Não foi encontrada uma solução ótima.")

if __name__ == "__main__":
    resolver_localizacao_estacoes()