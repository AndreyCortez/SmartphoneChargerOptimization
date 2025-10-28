import pandas as pd
import pulp
import math
import matplotlib.pyplot as plt
# Importado para desenhar os círculos
from matplotlib.patches import Circle

def calcular_distancia(ponto1, ponto2):
    """Calcula a distância Euclidiana entre dois pontos (x, y)."""
    return math.sqrt((ponto1[0] - ponto2[0])**2 + (ponto1[1] - ponto2[1])**2)

def resolver_localizacao_estacoes():
    """
    Resolve o problema de otimização de localização-alocação de estações
    para garantir que a capacidade não seja excedida.
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
    
    plot_df_demanda = df_demanda.copy()
    plot_df_candidatos = df_candidatos.copy()

    df_demanda.set_index('id', inplace=True)
    df_candidatos.set_index('id', inplace=True)

    d = df_demanda['demanda'].to_dict()
    c = df_candidatos['custo_fixo'].to_dict()
    K = df_candidatos['capacidade'].to_dict()

    loc_demanda = df_demanda.apply(lambda row: (row['localizacao_x'], row['localizacao_y']), axis=1).to_dict()
    loc_candidatos = df_candidatos.apply(lambda row: (row['localizacao_x'], row['localizacao_y']), axis=1).to_dict()

    # a_ij: Dicionário de conveniência
    a = {}
    # Lista de pares (i, j) convenientes para otimizar a criação de variáveis
    pares_convenientes = []
    for i in I:
        for j in J:
            dist = calcular_distancia(loc_demanda[i], loc_candidatos[j])
            if dist <= 50:
                a[(i, j)] = 1
                pares_convenientes.append((i, j))
            else:
                a[(i, j)] = 0

    # --- 4. Modelagem Matemática (NOVO MODELO) ---
    
    prob = pulp.LpProblem("Problema_Localizacao_Alocacao", pulp.LpMinimize)

    # Variável de Decisão (Instalação)
    x = pulp.LpVariable.dicts("x", J, cat=pulp.LpBinary)
    
    # Variável de Decisão (Alocação)
    # y_ij: Fração da demanda de i alocada para j
    # Apenas criamos variáveis para os pares (i,j) que são convenientes
    y = pulp.LpVariable.dicts("y", pares_convenientes, lowBound=0, cat=pulp.LpContinuous)

    # Função Objetivo (Mesma de antes)
    prob += pulp.lpSum(c[j] * x[j] for j in J), "Custo_Total_Instalacao"

    # --- 5. Adicionar Restrições (NOVO MODELO) ---
    
    # Restrição 1: Atendimento Total da Demanda
    for i in I:
        # A soma das frações alocadas de i para todas as estações j
        # convenientes deve ser 1 (100% da demanda de i atendida)
        prob += pulp.lpSum(y.get((i, j), 0) for j in J) == 1, f"Atendimento_Total_{i}"

    # Restrição 2: Capacidade da Estação (Anti-Sobrecarga)
    for j in J:
        # A soma da demanda absoluta (fração * demanda_i) alocada a j
        # (vinda de todos os i convenientes) não pode exceder a capacidade de j
        # se j for instalada (K_j * x_j)
        prob += pulp.lpSum(y.get((i, j), 0) * d[i] for i in I) <= K[j] * x[j], f"Capacidade_Estacao_{j}"

    # --- 6. Resolver o Problema ---
    
    print("Iniciando a resolução do problema (com alocação)...")
    prob.solve()

    # --- 7. Exibir Resultados ---
    
    print("="*30)
    print(f"Status da Solução: {pulp.LpStatus[prob.status]}")
    print("="*30)

    if pulp.LpStatus[prob.status] == 'Optimal':
        print(f"Custo Total Mínimo: {pulp.value(prob.objective):.2f}")
        print("\nEstações a serem instaladas (xj = 1) e suas cargas:")
        
        ids_instalados = []
        for j in J:
            if x[j].varValue == 1:
                ids_instalados.append(j)
                nome_local = df_candidatos.loc[j, 'nome']
                
                # --- LINHA CORRIGIDA ---
                # Calcular a carga total alocada a esta estação
                # Apenas somamos os (i, j) que estão nos pares convenientes
                carga_total_j = sum(y[(i, j)].varValue * d[i] for i in I if (i, j) in pares_convenientes)
                # --- FIM DA CORREÇÃO ---
                
                capacidade_j = K[j]
                
                print(f"  - {j}: {nome_local} | Carga: {carga_total_j:.1f} / {capacidade_j} ({(carga_total_j/capacidade_j)*100:.1f}%)")

        # --- 8. PLOTAR GRÁFICO (COM LINHAS DE ALOCAÇÃO) ---
        
        print("\nGerando gráfico da solução (com alocação)...")

        df_instalados = plot_df_candidatos[plot_df_candidatos['id'].isin(ids_instalados)]
        df_nao_instalados = plot_df_candidatos[~plot_df_candidatos['id'].isin(ids_instalados)]

        fig, ax = plt.subplots(figsize=(14, 10))

        # 1. Plotar Pontos de Demanda (I)
        ax.scatter(
            plot_df_demanda['localizacao_x'], 
            plot_df_demanda['localizacao_y'],
            c='blue', marker='o', s=80, label='Pontos de Demanda (I)', zorder=5
        )
        for _, row in plot_df_demanda.iterrows():
            ax.annotate(f"{row['id']} (D:{row['demanda']})", (row['localizacao_x'], row['localizacao_y']), 
                        textcoords="offset points", xytext=(0,-15), ha='center', color='darkblue')

        # 2. Plotar Candidatos Não Instalados (J)
        ax.scatter(
            df_nao_instalados['localizacao_x'], 
            df_nao_instalados['localizacao_y'],
            c='gray', marker='s', s=30, label='Candidatos Não Instalados', alpha=0.7, zorder=3
        )

        # 3. Plotar Estações Instaladas (x_j = 1)
        ax.scatter(
            df_instalados['localizacao_x'], 
            df_instalados['localizacao_y'],
            c='green', marker='s', s=100, edgecolor='black', label='Estações Instaladas (x_j = 1)', zorder=5
        )
        for _, row in df_instalados.iterrows():
            ax.annotate(row['id'], (row['localizacao_x'], row['localizacao_y']), 
                        textcoords="offset points", xytext=(5,5), ha='center', color='darkgreen', weight='bold')
            
            # Círculo de conveniência
            circle = plt.Circle((row['localizacao_x'], row['localizacao_y']), 
                                50, color='green', fill=False, linestyle='--', alpha=0.3)
            ax.add_patch(circle)

        # 4. (NOVO) Plotar Linhas de Alocação (y_ij)
        for (i, j) in pares_convenientes:
            fracao_alocada = y[(i, j)].varValue
            
            # Desenha a linha apenas se a alocação for significativa (ex: > 1%)
            if fracao_alocada > 0.01:
                ponto_i = loc_demanda[i]
                ponto_j = loc_candidatos[j]
                
                # A espessura da linha representa a fração da alocação
                ax.plot(
                    [ponto_i[0], ponto_j[0]], 
                    [ponto_i[1], ponto_j[1]],
                    color='purple', 
                    linestyle=':', 
                    linewidth=fracao_alocada * 2.5, # Linha mais grossa se alocar mais
                    alpha=0.6,
                    zorder=4 # Desenha atrás dos pontos, mas na frente do resto
                )

        
        # Configurações do Gráfico
        ax.set_title("Solução Ótima: Localização e Alocação de Estações")
        ax.set_xlabel("Localização X")
        ax.set_ylabel("Localização Y")
        ax.legend(loc='upper right')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_aspect('equal', adjustable='box') 
        
        plt.tight_layout() 
        
        nome_arquivo_saida = "resultado_localizacao_alocacao.png"
        plt.savefig(nome_arquivo_saida, dpi=300, bbox_inches='tight')
        print(f"\nGráfico salvo com sucesso em: {nome_arquivo_saida}")

        plt.show()

            
    elif pulp.LpStatus[prob.status] == 'Infeasible':
        print("O problema é inviável.")
        print("Isso significa que não há solução que satisfaça todas as restrições.")
        print("Possíveis causas:")
        print("  - Algum ponto de demanda (i) não pode ser coberto por NENHUMA estação (a_ij = 0 para todo j).")
        print("  - A capacidade total de TODAS as estações convenientes a 'i' é menor que a demanda 'd_i'.")
    else:
        print("Não foi encontrada uma solução ótima.")

if __name__ == "__main__":
    resolver_localizacao_estacoes()