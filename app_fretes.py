import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Matriz de Transportes", layout="wide")

st.title("📊 Matriz de Transportes: Comparativo Internacional")
st.markdown("Visualização estrutural dos modais de transporte (Rodoviário vs Ferroviário vs Aquaviário).")

# --- 1. DADOS ESTRUTURAIS (Inseridos Manualmente para evitar erro 404) ---
# Estes valores são aproximações baseadas no gráfico de referência que você enviou.
# Eles garantem que o app funcione instantaneamente.
dados = {
    'País': ['Rússia', 'Canadá', 'China', 'EUA', 'Brasil', 'Alemanha', 'França', 'Hungria', 'Bélgica', 'Dinamarca'],
    
    # Eixo X (Ferroviário)
    'Ferroviário (%)': [85, 65, 45, 42, 21, 19, 15, 35, 12, 10], 
    
    # Eixo Y (Rodoviário)
    'Rodoviário (%)':  [10, 25, 15, 38, 62, 65, 75, 60, 70, 78], 
    
    # Tamanho da Bolha (Aquaviário) - Ajustado para dar o efeito visual
    'Aquaviário (%)':  [5,  10, 40, 20, 17, 16, 10, 5,  18, 12] 
}

# Criar o DataFrame
df = pd.DataFrame(dados)

# --- 2. BARRA LATERAL (Filtros) ---
with st.sidebar:
    st.header("Configurações")
    
    # Filtro de Países
    todos_paises = sorted(df['País'].unique())
    paises_selecionados = st.multiselect(
        "Selecione os Países:",
        options=todos_paises,
        default=todos_paises # Por padrão, mostra todos
    )

# --- 3. PROCESSAMENTO E GRÁFICO ---
if paises_selecionados:
    df_filtrado = df[df['País'].isin(paises_selecionados)]
    
    # Cálculo para centralizar o texto (opcional)
    
    # --- GRÁFICO DE BOLHAS (SCATTER PLOT) ---
    fig = px.scatter(
        df_filtrado,
        x="Ferroviário (%)",
        y="Rodoviário (%)",
        size="Aquaviário (%)", # O tamanho da bolha
        text="País", # O nome do país aparece na bolha
        hover_name="País",
        hover_data=["Aquaviário (%)"],
        title="Matriz Modal de Transportes (Tamanho da bolha = % Aquaviário)",
        
        # DEFININDO AS CORES E ESTILO
        size_max=60, # Tamanho máximo das bolhas (aumente se quiser maiores)
        template="plotly_white",
        
        # Limites fixos para ficar igual à imagem (0 a 100%)
        range_x=[-5, 100], 
        range_y=[-5, 100]
    )

    # Melhorar a visualização dos textos
    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='DarkSlateGrey')) # Borda nas bolhas
    )

    # Configurar os Eixos e Setas (Para imitar a imagem)
    fig.update_layout(
        xaxis_title="<b>FERROVIÁRIO (%)</b>",
        yaxis_title="<b>RODOVIÁRIO (%)</b>",
        showlegend=False,
        height=600, # Altura do gráfico
        
        # Adicionar anotações (opcional, para explicar o gráfico)
        annotations=[
            dict(
                x=90, y=90,
                xref="x", yref="y",
                text="A Área do Círculo<br>representa a utilização<br>do modo Aquaviário",
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        ]
    )

    # Exibir no Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar a tabela de dados abaixo
    with st.expander("Ver Tabela de Dados"):
        st.dataframe(df_filtrado.set_index('País'))

else:
    st.warning("Selecione pelo menos um país na barra lateral.")