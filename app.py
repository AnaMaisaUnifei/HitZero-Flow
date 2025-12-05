import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="HitZero Flow - MVP V1.0 (Cálculo Guloso)", page_icon="🎀")

movimentos_db = [
    {"nome": "Elevator (Prep)", "tipo": "Stunt", "nivel": 1, "min_atletas": 4, "pontos": 10},
    {"nome": "Extension", "tipo": "Stunt", "nivel": 2, "min_atletas": 4, "pontos": 15},
    {"nome": "Liberty (Base Dupla)", "tipo": "Stunt", "nivel": 3, "min_atletas": 4, "pontos": 20},
    {"nome": "Full Down Stunt (Saída Twist)", "tipo": "Stunt", "nivel": 4, "min_atletas": 4, "pontos": 30},

    {"nome": "Single Base Extension", "tipo": "Stunt", "nivel": 3, "min_atletas": 3, "pontos": 25},
    {"nome": "Single Base Arabesque", "tipo": "Stunt", "nivel": 4, "min_atletas": 3, "pontos": 30},
    {"nome": "Rewind Stunt", "tipo": "Stunt", "nivel": 5, "min_atletas": 3, "pontos": 40},

    {"nome": "Basket Toss Straight", "tipo": "Toss", "nivel": 2, "min_atletas": 5, "pontos": 12},
    {"nome": "Basket Toss Toe Touch", "tipo": "Toss", "nivel": 3, "min_atletas": 5, "pontos": 18},
    {"nome": "Basket Toss com Full Twist", "tipo": "Toss", "nivel": 4, "min_atletas": 5, "pontos": 25},

    {"nome": "Pyramid 2-1", "tipo": "Pyramid", "nivel": 2, "min_atletas": 8, "pontos": 25},
    {"nome": "Pyramid 2-2-1", "tipo": "Pyramid", "nivel": 3, "min_atletas": 12, "pontos": 35},
    {"nome": "Pyramid Full Up to Extension", "tipo": "Pyramid", "nivel": 4, "min_atletas": 16, "pontos": 45},

    {"nome": "Toe Touch Jump Sequence", "tipo": "Jump", "nivel": 1, "min_atletas": 1, "pontos": 5},
    {"nome": "Pike Jump Sequence", "tipo": "Jump", "nivel": 1, "min_atletas": 1, "pontos": 5},
    {"nome": "High V Motion & Dance", "tipo": "Dance", "nivel": 1, "min_atletas": 1, "pontos": 2},
    {"nome": "Back Handspring", "tipo": "Tumbling", "nivel": 2, "min_atletas": 1, "pontos": 15},
    {"nome": "Standing Back Tuck", "tipo": "Tumbling", "nivel": 3, "min_atletas": 1, "pontos": 22},
]

# --- LÓGICA DO ALGORITMO ---
def gerar_rotina(nivel_time, qtd_atletas, incluir_tumbling):
    rotina = []
    
    #Filtra movimentos baseados em Nível, Atletas e Tumbling
    movimentos_possiveis = [
        m for m in movimentos_db 
        if m['nivel'] <= nivel_time 
        and m['min_atletas'] <= qtd_atletas 
        and (incluir_tumbling or m['tipo'] != 'Tumbling')
    ]
    
    if not movimentos_possiveis:
        return [], 0, "Nenhum movimento compatível encontrado."

    jumps_usados = 0
    piramides_usadas = set()
    elementos_obrigatorios = {'Jump'} 
    num_elementos = 12
    
    for i in range(num_elementos):
        candidatos = []
        
        if i >= (num_elementos - 2) and 'Jump' in elementos_obrigatorios:
            candidatos = [m for m in movimentos_possiveis if m['tipo'] == 'Jump']
        
        if jumps_usados >= 2:
            candidatos = [m for m in movimentos_possiveis if m['tipo'] != 'Jump']
        
        if not candidatos:
            candidatos = movimentos_possiveis

        if not candidatos: break

        escolha = random.choice(candidatos)
        
        if escolha['tipo'] == 'Pyramid':
            if escolha['nome'] in piramides_usadas:
                continue
            else:
                piramides_usadas.add(escolha['nome'])
        
        if escolha['tipo'] == 'Jump':
            jumps_usados += 1
            elementos_obrigatorios.discard('Jump')
            if jumps_usados == 2:
                movimentos_possiveis = [m for m in movimentos_possiveis if m['tipo'] != 'Jump']
        
        rotina.append(escolha)

    if 'Jump' in elementos_obrigatorios:
        jump_obg = random.choice([m for m in movimentos_db if m['tipo'] == 'Jump' and m['nivel'] <= nivel_time])
        rotina.insert(0, jump_obg)
        score_status = "Rotina gerada. Jump obrigatório foi inserido."
    else:
        score_status = "Sucesso. Todas as restrições cumpridas."

    score_total = sum(m['pontos'] for m in rotina)
    
    return rotina, score_total, score_status

# ---INTERFACE DO USUÁRIO (FRONT-END)---
st.title("🎀 HitZero Flow - MVP V1")
st.subheader("Sistema de Geração de Rotinas de Cheerleading")
st.markdown("---")

# Barra Lateral de Configuração (Inputs do Usuário)
st.sidebar.header("Configuração do Time")
nivel_selecionado = st.sidebar.selectbox("Nível Competitivo (IASF/Nacional)", [1, 2, 3, 4, 5])
qtd_atletas = st.sidebar.slider("Quantidade de Atletas Disponíveis (Total)", min_value=10, max_value=30, value=15)
incluir_tumbling = st.sidebar.checkbox("Incluir Tumbling (Ginástica de Solo)", value=True)

st.sidebar.markdown("---")
st.sidebar.info("Este é o MVP versão 1.0 para TFG1.")

# Botão de Ação "Gerar Rotina"
if st.button("Gerar Rotina", type="primary"):
    with st.spinner('Avaliando rotina com restrições...'):
        # Chama a função principal
        rotina_gerada, score, status = gerar_rotina(nivel_selecionado, qtd_atletas, incluir_tumbling)
        
        if rotina_gerada:
            st.success(f"Rotina Gerada: {status}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(label="Pontuação Estimada (Dificuldade)", value=f"{score} pontos")
            with col2:
                 st.metric(label="Elementos Selecionados", value=f"{len(rotina_gerada)}")

            #Prepara a exibição dos dados na tabela
            df_rotina = pd.DataFrame(rotina_gerada)

            # Cálculo de formações possíveis
            def calcular_formacoes(row, qtd_total_atletas):
                if row['tipo'] in ['Stunt', 'Toss', 'Pyramid']:
                    min_atletas = row['min_atletas']
                    return qtd_total_atletas // min_atletas
                # Para Jump, Dance, Tumbling, assume-se 1 atleta ou 1 grupo na contagem
                return 1

            df_rotina['Formações Possíveis'] = df_rotina.apply(
                lambda row: calcular_formacoes(row, qtd_atletas), axis=1
            )
            
            df_display = df_rotina[['nome', 'tipo', 'nivel', 'min_atletas', 'pontos', 'Formações Possíveis']]
            df_display.columns = ['Movimento', 'Categoria', 'Nível (Dificuldade)', 'Min. Atletas', 'Pontos', 'Formações Possíveis']
            
            st.subheader("Sequência de Elementos")
            st.table(df_display.style.set_properties(**{'font-size': '12pt'}).hide(axis='index'))
            
            # --- Gráfico ---
            st.subheader("Frequência por Categoria")
            contagem_categorias = df_rotina['tipo'].value_counts()
            st.bar_chart(contagem_categorias)
            st.caption("Frequência dos Elementos na Rotina por Categoria.")
            
        else:
            st.error(f"Não foi possível gerar uma rotina com esses parâmetros. Status: {status}")

st.markdown("---")
st.caption("HitZero Flow v1.0 - TCC - Ciência da Computação - UNIFEI")