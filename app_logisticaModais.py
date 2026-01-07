import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Logística e Modais (ITF 69)", layout="wide")

# --- CSS para dar destaque ao botão ---
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

st.title("📊 Matriz de Transportes: ITF (69 Países Membros)")
st.markdown("""
Este painel apresenta a distribuição estimada da matriz de transporte de cargas para os **69 países membros** do International Transport Forum.
**O tamanho da bolha representa a participação do modal Aquaviário/Hidroviário.**
""")

# --- 1. BASE DE DADOS COMPLETA (69 PAÍSES) ---
# Simulação de dados para 2015 e 2023

paises_itf = [
    'Albania', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium', 
    'Bosnia-Herzegovina', 'Brazil', 'Bulgaria', 'Cambodia', 'Canada', 'Chile', 'China', 'Colombia', 
    'Costa Rica', 'Croatia', 'Czechia', 'Denmark', 'Dominican Republic', 'Estonia', 'Finland', 'France', 
    'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'India', 'Ireland', 'Israel', 'Italy', 
    'Japan', 'Kazakhstan', 'Korea', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 
    'Mexico', 'Moldova', 'Mongolia', 'Montenegro', 'Morocco', 'Netherlands', 'New Zealand', 'North Macedonia', 
    'Norway', 'Oman', 'Poland', 'Portugal', 'Romania', 'Russia', 'Saudi Arabia', 'Serbia', 'Slovakia', 
    'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Tunisia', 'Turkey', 'Ukraine', 'United Arab Emirates', 
    'United Kingdom', 'United States', 'Uzbekistan'
]

@st.cache_data
def gerar_base_dados():
    lista_dados = []
    for p in paises_itf:
        # --- Simulação 2015 ---
        dados_2015 = gerar_dados_pais(p, 2015)
        lista_dados.append(dados_2015)
        
        # --- Simulação 2023 ---
        dados_2023 = gerar_dados_pais(p, 2023)
        lista_dados.append(dados_2023)
    
    return pd.DataFrame(lista_dados)

def gerar_dados_pais(pais, ano):
    # Lógica de estimativa baseada em geografia
    road = 70; rail = 20; water = 10
    
    # Grupo 1: Alta Ferrovia
    if pais in ['Russia', 'Kazakhstan', 'Ukraine', 'Belarus', 'Uzbekistan', 'Latvia', 'Lithuania', 'Estonia', 'Canada', 'USA', 'Australia', 'China', 'India', 'Mongolia']:
        rail += 35; road -= 30
    
    # Grupo 2: Alto Aquaviário
    if pais in ['Netherlands', 'Belgium', 'Romania', 'China', 'Germany', 'USA', 'Vietnam', 'Cambodia']:
        water += 25; road -= 15; rail -= 10

    # Grupo 3: Ilhas/Pequenos (Pouca ferrovia)
    if pais in ['Iceland', 'Malta', 'Cyprus', 'Ireland', 'New Zealand', 'Dominican Republic']:
        rail = 0; water += 5; road = 95 - water

    # Grupo 4: América Latina (Forte Rodoviário)
    if pais in ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Mexico', 'Costa Rica']:
        road += 15; rail = max(5, rail - 10); water = max(1, water - 5)
        if pais == 'Brazil': rail = 21; road = 62; water = 17

    # Tendência temporal (2023 tem mais rodovia que 2015 na maioria)
    if ano == 2015:
        rail += 2; road -= 2 # Em 2015 o trem era ligeiramente maior
    
    # Normalização para 100%
    total = road + rail + water
    road = round((road / total) * 100, 1)
    rail = round((rail / total) * 100, 1)
    water = round(100 - road - rail, 1)

    return {'País': pais, 'Ferroviário (%)': rail, 'Rodoviário (%)': road, 'Aquaviário (%)': water, 'Ano': ano}

# Carrega os dados
df = gerar_base_dados()

# --- 2. BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    
    # --- BOTÃO DE AÇÃO (ATUALIZAÇÃO) ---
    # Usamos session_state para controlar o ano através do botão
    if 'ano_atual' not in st.session_state:
        st.session_state.ano_atual = 2015 # Começa em 2015 por padrão

    if st.button("🔄 Carregar Última Atualização (2023)"):
        st.session_state.ano_atual = 2023
        st.success("Dados atualizados para 2023!")

    st.divider()
    
    st.subheader("Linha do Tempo")
    # O slider agora obedece ao session_state
    ano_selecionado = st.select_slider(
        "Ano de Referência:", 
        options=[2015, 2023], 
        value=st.session_state.ano_atual,
        key="slider_ano" # Chave para sincronizar, mas controlamos via value
    )
    
    # Se o usuário mexer no slider manualmente, atualizamos o estado
    if ano_selecionado != st.session_state.ano_atual:
        st.session_state.ano_atual = ano_selecionado
        st.rerun() # Recarrega a página para garantir a sincronia

    # Filtrar DataFrame pelo ano
    df_ano = df[df['Ano'] == st.session_state.ano_atual]

    st.divider()
    
    # --- FILTRO DE PAÍSES ---
    st.subheader("Filtro de Países")
    todos_paises = sorted(df_ano['País'].unique())
    
    # Sugestão inicial
    sugestao = ['Brazil', 'USA', 'China', 'Germany', 'India', 'Russia', 'Argentina', 'France']
    padrao = [p for p in sugestao if p in todos_paises]
    
    usar_todos = st.checkbox("Selecionar Todos (69 Países)", value=False)
    
    if usar_todos:
        paises_selecionados = todos_paises
    else:
        paises_selecionados = st.multiselect(
            "Selecione os Países:",
            options=todos_paises,
            default=padrao
        )

# --- 3. GRÁFICO PRINCIPAL ---
if paises_selecionados:
    df_filtrado = df_ano[df_ano['País'].isin(paises_selecionados)]
    
    # Gráfico
    fig = px.scatter(
        df_filtrado,
        x="Ferroviário (%)",
        y="Rodoviário (%)",
        size="Aquaviário (%)",
        color="País",
        text="País",
        hover_name="País",
        hover_data=["Aquaviário (%)"],
        title=f"Matriz Modal ({st.session_state.ano_atual}) - ITF 69 Membros",
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
        xaxis_title="<b>FERROVIÁRIO (%)</b>",
        yaxis_title="<b>RODOVIÁRIO (%)</b>",
        showlegend=False,
        height=700,
        transition={'duration': 800} # Animação suave na troca de ano
    )

    # Linhas auxiliares
    fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line=dict(color="LightGray", dash="dot"))

    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    with st.expander(f"📋 Ver Tabela de Dados ({len(df_filtrado)} países)"):
        st.dataframe(
            df_filtrado[['País', 'Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']]
            .sort_values('País')
            .set_index('País')
            .style.format("{:.1f}%")
        )

else:
    st.warning("⚠️ Selecione pelo menos um país na barra lateral para visualizar o gráfico.")