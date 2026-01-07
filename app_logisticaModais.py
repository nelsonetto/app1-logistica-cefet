import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuração da página
st.set_page_config(page_title="Modais Logísticos (Global)", layout="wide")

# --- CSS para estilo do botão ---
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #0099ff;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz de Transportes: Modais Logísticos")
st.markdown("""
Este painel apresenta a matriz de transporte comparativa.
**Fonte:** Dados oficiais da OCDE (arquivo importado) + Estimativas para Key Partners (Brasil, China, etc.).
**Eixos:** X = Ferroviário | Y = Rodoviário | Bolha = Aquaviário
""")

# --- 1. DADOS HÍBRIDOS (OCDE REAL + COMPLEMENTAR) ---

# Parte A: Dados Reais do seu Arquivo (Europa, América do Norte, etc.)
DATA_REAL = """País,Ano,Ferroviário (%),Rodoviário (%),Aquaviário (%),Total
Austria,2023,43.1,54.4,2.5,46902.5
Austria,2024,44.1,53.2,2.7,47635.0
Belgium,2023,0.0,83.2,16.8,38721.0
Belgium,2024,0.0,82.0,18.0,38000.0
Canada,2023,100.0,0.0,0.0,424846.0
Canada,2024,60.0,40.0,0.0,700000.0
Czechia,2023,18.8,81.1,0.0,79861.9
Czechia,2024,17.8,82.2,0.0,85612.5
Denmark,2023,10.4,89.6,0.0,18311.0
Denmark,2024,9.7,90.3,0.0,18452.0
Finland,2023,21.8,77.6,0.6,36406.4
Finland,2024,22.5,77.3,0.2,35819.6
France,2023,14.8,82.4,2.9,199201.0
France,2024,15.6,81.6,2.8,206202.0
Germany,2023,27.9,62.9,9.2,449878.1
Germany,2024,28.1,62.2,9.7,449285.3
Hungary,2023,23.2,73.9,2.9,45128.5
Hungary,2024,22.5,74.1,3.3,46169.2
Italy,2023,13.3,86.7,0.0,167523.0
Italy,2024,13.0,87.0,0.0,175577.0
Japan,2023,7.2,92.8,0.0,246485.0
Japan,2024,7.1,92.9,0.0,249740.0
Latvia,2023,28.2,71.8,0.0,18393.0
Latvia,2024,19.1,80.9,0.0,18417.0
Lithuania,2023,9.1,90.9,0.0,69410.0
Lithuania,2024,8.2,91.8,0.0,72159.6
Mexico,2023,100.0,0.0,0.0,92132.2
Mexico,2024,25.0,75.0,0.0,350000.0
Netherlands,2023,5.9,56.5,37.6,110719.0
Netherlands,2024,5.5,56.5,37.9,111225.0
Poland,2023,29.1,70.8,0.1,210147.1
Poland,2024,28.8,71.0,0.1,200554.8
Romania,2023,14.1,72.6,13.3,89851.0
Romania,2024,12.2,74.0,13.8,90996.0
Spain,2023,1.6,98.4,0.0,267761.9
Spain,2024,1.4,98.6,0.0,275487.0
Sweden,2023,34.1,65.7,0.2,64456.2
Sweden,2024,34.6,65.0,0.3,62946.2
Switzerland,2023,40.1,59.8,0.1,25841.5
Switzerland,2024,40.0,59.6,0.4,26000.0
United States,2023,37.0,63.0,0.0,5610333.0
United States,2024,36.5,56.5,7.0,6100000.0"""

# Parte B: Dados Complementares (Brasil, Rússia, China, UK)
# Adicionados manualmente para corrigir a ausência no arquivo original
DATA_EXTRA = """País,Ano,Ferroviário (%),Rodoviário (%),Aquaviário (%),Total
Brazil,2023,21.0,62.0,17.0,100
Brazil,2024,21.5,61.5,17.0,100
Russia,2023,86.0,10.0,4.0,100
Russia,2024,85.5,10.5,4.0,100
China,2023,30.0,50.0,20.0,100
China,2024,29.0,51.0,20.0,100
United Kingdom,2023,9.0,90.0,1.0,100
United Kingdom,2024,9.5,89.5,1.0,100
India,2023,70.0,25.0,5.0,100
India,2024,68.0,27.0,5.0,100
Australia,2023,55.0,35.0,10.0,100
Australia,2024,54.0,36.0,10.0,100"""

@st.cache_data
def carregar_dados_hibridos():
    # Carrega as duas partes e junta
    df_real = pd.read_csv(io.StringIO(DATA_REAL))
    df_extra = pd.read_csv(io.StringIO(DATA_EXTRA))
    
    # Concatena tudo num único DataFrame
    df_final = pd.concat([df_real, df_extra], ignore_index=True)
    return df_final

df = carregar_dados_hibridos()

# --- 2. CONTROLES DE ESTADO ---
if 'ano_atual' not in st.session_state:
    st.session_state.ano_atual = 2024

def set_ano_maximo():
    st.session_state.ano_atual = 2024

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    
    st.button("🔄 Carregar Última Atualização (2024)", on_click=set_ano_maximo)

    st.divider()
    
    st.subheader("Linha do Tempo")
    ano_selecionado = st.select_slider(
        "Ano de Referência:", 
        options=[2023, 2024], # Focando nos anos mais recentes
        value=st.session_state.ano_atual,
        key="ano_slider" 
    )
    
    if ano_selecionado != st.session_state.ano_atual:
        st.session_state.ano_atual = ano_selecionado
        st.rerun()

    st.divider()
    
    st.subheader("Filtro de Países")
    todos_paises = sorted(df['País'].unique())
    
    # Sugestão com os países que você quer ver
    sugestao = ['Brazil', 'United States', 'China', 'Russia', 'Germany', 'United Kingdom']
    padrao = [p for p in sugestao if p in todos_paises]
    
    paises_selecionados = st.multiselect(
        "Selecione os Países:",
        options=todos_paises,
        default=padrao,
        key="multiselect_paises"
    )

# --- 3. GRÁFICO ---
df_ano = df[df['Ano'] == st.session_state.ano_atual]

if paises_selecionados:
    df_filtrado = df_ano[df_ano['País'].isin(paises_selecionados)]
    
    if not df_filtrado.empty:
        fig = px.scatter(
            df_filtrado,
            x="Ferroviário (%)",
            y="Rodoviário (%)",
            size="Aquaviário (%)",
            color="País",
            text="País",
            hover_name="País",
            hover_data=["Aquaviário (%)", "Ano"],
            title=f"Matriz de Transportes ({st.session_state.ano_atual})",
            size_max=60,
            template="plotly_white",
            range_x=[-5, 105], 
            range_y=[-5, 105],
        )

        fig.update_traces(
            textposition='top center',
            marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.9)
        )

        fig.update_layout(
            xaxis_title="<b>Porcentagem do Modal Ferroviário</b>",
            yaxis_title="<b>Modal Rodoviário</b>",
            xaxis=dict(dtick=10, tickmode='linear'),
            yaxis=dict(dtick=10, tickmode='linear'),
            showlegend=False,
            height=700,
            transition={'duration': 500, 'easing': 'cubic-in-out'}
        )

        fig.add_shape(type="line", x0=0, y0=100, x1=100, y1=0, line=dict(color="LightGray", dash="dot"))

        st.plotly_chart(fig, use_container_width=True)

        with st.expander(f"📋 Ver Detalhes ({len(df_filtrado)} países)"):
            st.dataframe(
                df_filtrado[['País', 'Ano', 'Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']]
                .sort_values('País')
                .set_index('País')
                .style.format("{:.1f}%")
            )
    else:
        st.warning(f"Sem dados para {st.session_state.ano_atual}.")

else:
    st.info("👋 Selecione países na barra lateral.")