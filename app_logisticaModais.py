import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Logística e Modais", layout="wide")

st.title("📊 Matriz de Transportes: Comparativo Internacional")
st.markdown("""
Este painel apresenta a distribuição da matriz de transporte de cargas entre os modais.
**O tamanho da bolha representa a participação do modal Aquaviário/Hidroviário.**
""")

# --- 1. DADOS PADRÃO (BASE EXPANDIDA 30 PAÍSES) ---
# Dados aproximados para garantir o funcionamento sem depender de API externa
dados_padrao = {
    'País': [
        'Rússia', 'Canadá', 'China', 'EUA', 'Brasil', 
        'Alemanha', 'França', 'Hungria', 'Bélgica', 'Dinamarca',
        'Austrália', 'Índia', 'Japão', 'Reino Unido', 'Itália',
        'Espanha', 'Holanda', 'Polônia', 'México', 'Argentina',
        'África do Sul', 'Turquia', 'Suécia', 'Noruega', 'Finlândia',
        'Suíça', 'Áustria', 'Coreia do Sul', 'Indonésia', 'Arábia Saudita'
    ],
    # Eixo X
    'Ferroviário (%)': [
        85, 60, 48, 40, 21, 
        19, 15, 35, 12, 10,
        55, 70, 30, 10, 14,
        5, 5, 25, 26, 15,
        30, 5, 35, 15, 27,
        40, 45, 20, 1, 15
    ], 
    # Eixo Y
    'Rodoviário (%)': [
        10, 30, 35, 45, 62, 
        65, 78, 60, 68, 85,
        35, 25, 60, 85, 85,
        90, 45, 74, 73, 80,
        69, 90, 60, 40, 68,
        58, 50, 75, 90, 84
    ],
    # Tamanho da Bolha
    'Aquaviário (%)': [
        5, 10, 17, 15, 17, 
        16, 7, 5, 20, 5,
        10, 5, 10, 5, 1,
        5, 50, 1, 1, 5,
        1, 5, 5, 45, 5,
        2, 5, 5, 9, 1
    ]
}

# --- 2. BARRA LATERAL (UPLOAD E FILTROS) ---
with st.sidebar:
    st.header("📂 Fonte de Dados")
    
    # Opção para Upload
    arquivo_upload = st.file_uploader("Carregar Excel ou CSV (Opcional)", type=['csv', 'xlsx'])
    
    if arquivo_upload is not None:
        try:
            if arquivo_upload.name.endswith('.csv'):
                df = pd.read_csv(arquivo_upload)
            else:
                df = pd.read_excel(arquivo_upload)
            st.success("Arquivo carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            df = pd.DataFrame(dados_padrao)
    else:
        df = pd.DataFrame(dados_padrao)

    st.divider()
    
    st.header("Filtros de Visualização")
    
    # Filtro de Países
    if not df.empty and 'País' in df.columns:
        todos_paises = sorted(df['País'].unique())
        
        # Sugestão de países iniciais para o gráfico não abrir vazio
        sugestao = ['Brasil', 'EUA', 'China', 'Rússia', 'Alemanha', 'França', 'Canadá']
        padrao = [p for p in sugestao if p in todos_paises]
        
        paises_selecionados = st.multiselect(
            "Selecione os Países:",
            options=todos_paises,
            default=padrao if padrao else todos_paises[:5]
        )
    else:
        st.error("O arquivo carregado não tem a coluna 'País'.")
        paises_selecionados = []

# --- 3. GRÁFICO DE BOLHAS (CONFIGURAÇÃO VISUAL) ---
if paises_selecionados:
    df_filtrado = df[df['País'].isin(paises_selecionados)]
    
    # Validação das colunas
    cols_necessarias = ['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']
    
    if all(col in df_filtrado.columns for col in cols_necessarias):
        
        # Criação do Gráfico
        fig = px.scatter(
            df_filtrado,
            x="Ferroviário (%)",
            y="Rodoviário (%)",
            size="Aquaviário (%)",
            color="País", # <--- COR DISTINTA PARA CADA PAÍS
            text="País",
            hover_name="País",
            hover_data=["Aquaviário (%)"],
            title="Matriz Modal de Transportes (Tamanho da bolha = % Aquaviário)",
            size_max=60, # Tamanho máximo visual das bolhas
            template="plotly_white",
            # Fixar eixos de 0 a 105% para manter a referência visual
            range_x=[-5, 105], 
            range_y=[-5, 105]
        )

        # Ajustes finos visuais
        fig.update_traces(
            textposition='top center',
            marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.9)
        )

        fig.update_layout(
            xaxis_title="<b>FERROVIÁRIO (%)</b>",
            yaxis_title="<b>RODOVIÁRIO (%)</b>",
            showlegend=False, # Legenda desativada pois o nome já está na bolha
            height=650
        )

        # Adicionar linha tracejada diagonal (opcional, apenas estético)
        fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line=dict(color="LightGray", dash="dot"))

        st.plotly_chart(fig, use_container_width=True)

        # Mostrar Dados em Tabela
        with st.expander("Ver Tabela de Dados"):
            st.dataframe(df_filtrado.set_index('País'))
            
    else:
        st.error(f"As colunas do arquivo devem ser: {cols_necessarias}")
else:
    st.warning("Selecione pelo menos um país na barra lateral.")