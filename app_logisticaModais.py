import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Logística e Modais (ITF 69)", layout="wide")

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

st.title("📊 Matriz de Transportes: ITF (69 Países Membros)")
st.markdown("""
Este painel apresenta a evolução da matriz de transporte entre **2015 e 2023**.
**O tamanho da bolha representa a participação do modal Aquaviário/Hidroviário.**
""")

# --- 1. BASE DE DADOS COMPLETA (INTERPOLAÇÃO 2015-2023) ---

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

def obter_perfil_base(pais):
    """Define os pontos de partida (2015) e chegada (2023) para cada país"""
    # Valores base genéricos
    r15, tr15, wa15 = 68, 22, 10  # 2015
    r23, tr23, wa23 = 70, 20, 10  # 2023 (Tendência global leve para rodovia)

    # Ajustes Geográficos Específicos
    
    # Grupo Ferroviário (Leste Europeu, Rússia, América do Norte)
    if pais in ['Russia', 'Kazakhstan', 'Ukraine', 'Belarus', 'Uzbekistan', 'Latvia', 'Lithuania', 'Estonia', 'Mongolia']:
        r15, tr15 = 15, 80; r23, tr23 = 20, 75 # Leve queda da ferrovia
    elif pais in ['Canada', 'USA', 'Australia', 'China', 'India']:
        r15, tr15 = 40, 45; r23, tr23 = 45, 40

    # Grupo Aquaviário (Holanda, Bélgica, etc)
    if pais in ['Netherlands', 'Belgium', 'Romania', 'Germany', 'Vietnam', 'China']:
        wa15, wa23 = 40, 42
        r15 = 100 - wa15 - tr15; r23 = 100 - wa23 - tr23
    
    # Grupo Ilhas (Sem trem)
    if pais in ['Iceland', 'Malta', 'Cyprus', 'Ireland', 'New Zealand', 'Dominican Republic']:
        tr15 = 0; tr23 = 0
        wa15 = 5; wa23 = 5
        r15 = 95; r23 = 95

    # América Latina (Brasil e vizinhos)
    if pais in ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Mexico', 'Costa Rica']:
        r15, tr15, wa15 = 60, 23, 17 # 2015
        r23, tr23, wa23 = 62, 21, 17 # 2023 (Brasil estagnado/leve piora ferrovias)
        
        if pais != 'Brazil': # Outros latinos tem menos trem e agua que o Brasil
             wa15 = 2; wa23 = 2
             r15 += 15; r23 += 15

    return (r15, tr15, wa15), (r23, tr23, wa23)

@st.cache_data
def gerar_dados_anuais():
    lista_completa = []
    
    # Loop por todos os anos para preencher o "vazio"
    anos = range(2015, 2024) # 2015 a 2023
    
    for pais in paises_itf:
        (r_start, t_start, w_start), (r_end, t_end, w_end) = obter_perfil_base(pais)
        
        for ano in anos:
            # Cálculo de Interpolação Linear (A animação matemática)
            progresso = (ano - 2015) / (2023 - 2015) # Vai de 0.0 a 1.0
            
            rail = t_start + (t_end - t_start) * progresso
            water = w_start + (w_end - w_start) * progresso
            road = 100 - rail - water # Garante soma 100%
            
            lista_completa.append({
                'País': pais,
                'Ano': ano,
                'Ferroviário (%)': round(rail, 1),
                'Rodoviário (%)': round(road, 1),
                'Aquaviário (%)': round(water, 1)
            })
            
    return pd.DataFrame(lista_completa)

# Carregar Dados
df = gerar_dados_anuais()

# --- 2. CONTROLES DE ESTADO (SESSION STATE) ---
# Inicializa variáveis para manter a memória do app
if 'ano_atual' not in st.session_state:
    st.session_state.ano_atual = 2023

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    
    # Botão de Reset Rápido
    if st.button("🔄 Carregar Última Atualização (2023)"):
        st.session_state.ano_atual = 2023
        # O slider vai ler essa variável automaticamente abaixo

    st.divider()
    
    st.subheader("Linha do Tempo")
    
    # Slider conectado ao session_state
    # Se mudar aqui, muda a variável global. Se clicar no botão acima, o slider move sozinho.
    ano_selecionado = st.select_slider(
        "Ano de Referência:", 
        options=range(2015, 2024), # Agora mostra TODOS os anos
        value=st.session_state.ano_atual,
        key="slider_ano_key"
    )
    
    # Atualiza o estado se o usuário mexer no slider
    st.session_state.ano_atual = ano_selecionado

    st.divider()
    
    # --- FILTRO DE PAÍSES (CORRIGIDO PARA NÃO RESETAR) ---
    st.subheader("Filtro de Países")
    
    # Lista única de países (não muda com o ano, então é estável)
    todos_paises = sorted(paises_itf)
    
    # Sugestão inicial (só roda na primeira vez que abre o app)
    sugestao = ['Brazil', 'USA', 'China', 'Germany', 'Russia', 'Argentina']
    padrao = [p for p in sugestao if p in todos_paises]
    
    # O SEGREDO DO "NÃO RESETAR": Usar uma chave fixa (key)
    # Quando o script roda de novo (muda o ano), o Streamlit vê a mesma key 
    # e mantém o que o usuário escolheu, ignorando o 'default'.
    paises_selecionados = st.multiselect(
        "Selecione os Países:",
        options=todos_paises,
        default=padrao,
        key="multiselect_paises" 
    )

# --- 3. FILTRAGEM E GRÁFICO ---

# Pega apenas os dados do ano selecionado no slider/botão
df_ano = df[df['Ano'] == st.session_state.ano_atual]

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
        hover_data=["Aquaviário (%)", "Ano"],
        title=f"Matriz Modal ({st.session_state.ano_atual}) - ITF 69 Membros",
        size_max=60,
        template="plotly_white",
        # Eixos fixos são CRUCIAIS para ver a "animação" das bolhas se mexendo
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
        # Animação suave na transição dos pontos
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )

    # Adicionar linha diagonal (Limites matemáticos)
    fig.add_shape(type="line", x0=0, y0=100, x1=100, y0=0, line=dict(color="LightGray", dash="dot"))

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Dados
    with st.expander(f"📋 Ver Detalhes ({len(df_filtrado)} países)"):
        st.dataframe(
            df_filtrado[['País', 'Ano', 'Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']]
            .sort_values('País')
            .set_index('País')
            .style.format({"Rodoviário (%)": "{:.1f}%", "Ferroviário (%)": "{:.1f}%", "Aquaviário (%)": "{:.1f}%"})
        )

else:
    st.info("👋 Selecione um ou mais países na barra lateral para começar a análise.")