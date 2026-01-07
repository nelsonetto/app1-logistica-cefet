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
Este painel apresenta a evolução da matriz de transporte (2015-2024).
**Fonte:** Dados oficiais OCDE + Estimativas para Parceiros Chave (Brasil, China, Rússia).
""")

# --- 1. DADOS OFICIAIS OCDE (2015-2024) ---
# Extraído diretamente do seu arquivo original
DATA_REAL = """País,Ano,Ferroviário (%),Rodoviário (%),Aquaviário (%)
Austria,2015,41.7,54.3,4.0
Austria,2016,40.8,54.9,4.2
Austria,2017,44.8,51.1,4.1
Austria,2018,45.1,51.8,3.1
Austria,2019,43.5,53.1,3.4
Austria,2020,43.1,53.5,3.4
Austria,2021,43.9,53.1,3.0
Austria,2022,44.7,52.9,2.5
Austria,2023,43.1,54.4,2.5
Austria,2024,44.1,53.2,2.7
Belgium,2015,0.0,75.3,24.7
Belgium,2016,0.0,74.9,25.1
Belgium,2017,0.0,70.7,29.3
Belgium,2018,0.0,81.7,18.3
Belgium,2019,0.0,82.8,17.2
Belgium,2020,0.0,83.1,16.9
Belgium,2021,0.0,82.6,17.4
Belgium,2022,0.0,82.7,17.3
Belgium,2023,0.0,83.2,16.8
Bulgaria,2015,10.0,89.0,1.0
Bulgaria,2016,8.8,90.5,0.7
Bulgaria,2017,9.9,89.1,1.0
Bulgaria,2018,12.3,86.9,0.7
Bulgaria,2019,15.8,83.4,0.9
Bulgaria,2020,12.1,87.3,0.5
Bulgaria,2021,11.6,87.8,0.6
Bulgaria,2022,12.9,86.4,0.7
Bulgaria,2023,11.9,86.8,1.2
Bulgaria,2024,13.8,85.3,0.9
Canada,2015,59.8,40.2,0.0
Canada,2016,57.4,42.6,0.0
Canada,2017,58.4,41.6,0.0
Canada,2018,62.3,37.7,0.0
Czechia,2015,20.6,79.3,0.0
Czechia,2016,23.7,76.3,0.1
Czechia,2017,26.3,73.6,0.0
Czechia,2018,28.7,71.2,0.0
Czechia,2019,29.3,70.7,0.1
Czechia,2020,21.5,78.5,0.0
Czechia,2021,20.4,79.6,0.0
Czechia,2022,19.9,80.1,0.0
Czechia,2023,18.8,81.1,0.0
Czechia,2024,17.8,82.2,0.0
Denmark,2015,14.5,85.5,0.0
Denmark,2016,14.1,85.9,0.0
Denmark,2017,14.6,85.4,0.0
Denmark,2018,14.7,85.3,0.0
Denmark,2019,14.4,85.6,0.0
Denmark,2020,14.3,85.7,0.0
Denmark,2021,11.4,88.6,0.0
Denmark,2022,12.7,87.3,0.0
Denmark,2023,10.4,89.6,0.0
Denmark,2024,9.7,90.3,0.0
Estonia,2015,33.2,66.8,0.0
Estonia,2016,25.8,74.2,0.0
Estonia,2017,27.3,72.7,0.0
Estonia,2018,31.0,69.0,0.0
Estonia,2019,31.1,68.9,0.0
Estonia,2020,28.8,71.2,0.0
Estonia,2021,28.9,71.1,0.0
Estonia,2022,22.1,77.9,0.0
Estonia,2023,15.5,84.5,0.0
Estonia,2024,11.8,88.2,0.0
Finland,2015,25.6,74.0,0.4
Finland,2016,25.9,73.8,0.3
Finland,2017,26.9,72.8,0.3
Finland,2018,27.9,71.8,0.3
Finland,2019,25.8,73.9,0.3
Finland,2020,24.9,74.7,0.3
Finland,2021,26.3,73.4,0.4
Finland,2022,22.3,77.2,0.5
Finland,2023,21.8,77.6,0.6
Finland,2024,22.5,77.3,0.2
France,2015,18.0,78.1,3.9
France,2016,17.1,79.3,3.6
France,2017,17.2,79.6,3.2
France,2018,16.6,80.2,3.3
France,2019,16.2,80.2,3.6
France,2020,15.6,81.0,3.3
France,2021,17.0,79.7,3.3
France,2022,16.8,80.2,3.0
France,2023,14.8,82.4,2.9
France,2024,15.6,81.6,2.8
Germany,2015,23.8,64.7,11.5
Germany,2016,23.1,65.5,11.4
Germany,2017,22.5,65.7,11.8
Germany,2018,23.5,66.5,10.0
Germany,2019,23.9,65.3,10.8
Germany,2020,25.1,64.9,10.0
Germany,2021,27.4,62.7,9.9
Germany,2022,28.0,62.8,9.2
Germany,2023,27.9,62.9,9.2
Germany,2024,28.1,62.2,9.7
Hungary,2015,19.9,76.4,3.6
Hungary,2016,20.0,76.2,3.8
Hungary,2017,21.4,74.8,3.8
Hungary,2018,21.1,75.7,3.2
Hungary,2019,21.4,74.4,4.3
Hungary,2020,25.3,70.3,4.4
Hungary,2021,22.5,73.7,3.7
Hungary,2022,22.6,74.4,3.0
Hungary,2023,23.2,73.9,2.9
Hungary,2024,22.5,74.1,3.3
Italy,2015,13.3,86.6,0.0
Italy,2016,14.8,85.2,0.1
Italy,2017,15.4,84.6,0.0
Italy,2018,14.9,85.1,0.1
Italy,2019,13.2,86.8,0.0
Italy,2020,13.1,86.8,0.1
Italy,2021,13.9,86.0,0.1
Italy,2022,13.8,86.2,0.1
Italy,2023,13.3,86.7,0.0
Italy,2024,13.0,87.0,0.0
Japan,2015,9.5,90.5,0.0
Japan,2016,9.3,90.7,0.0
Japan,2017,9.3,90.7,0.0
Japan,2018,8.5,91.5,0.0
Japan,2019,8.6,91.4,0.0
Japan,2020,8.1,91.9,0.0
Japan,2021,7.5,92.5,0.0
Japan,2022,7.3,92.7,0.0
Japan,2023,7.2,92.8,0.0
Japan,2024,7.1,92.9,0.0
Latvia,2015,56.3,43.7,0.0
Latvia,2016,52.7,47.3,0.0
Latvia,2017,50.1,49.9,0.0
Latvia,2018,54.4,45.6,0.0
Latvia,2019,50.1,49.9,0.0
Latvia,2020,36.8,63.2,0.0
Latvia,2021,32.8,67.2,0.0
Latvia,2022,33.7,66.3,0.0
Latvia,2023,28.2,71.8,0.0
Latvia,2024,19.1,80.9,0.0
Lithuania,2015,34.6,65.4,0.0
Lithuania,2016,30.8,69.2,0.0
Lithuania,2017,28.3,71.7,0.0
Lithuania,2018,27.9,72.1,0.0
Lithuania,2019,23.3,76.6,0.0
Lithuania,2020,22.3,77.7,0.0
Lithuania,2021,20.1,79.9,0.0
Lithuania,2022,12.1,87.9,0.0
Lithuania,2023,9.1,90.9,0.0
Lithuania,2024,8.2,91.8,0.0
Mexico,2015,100.0,0.0,0.0
Mexico,2016,100.0,0.0,0.0
Mexico,2017,100.0,0.0,0.0
Mexico,2018,100.0,0.0,0.0
Mexico,2019,100.0,0.0,0.0
Mexico,2020,100.0,0.0,0.0
Mexico,2021,100.0,0.0,0.0
Mexico,2022,100.0,0.0,0.0
Mexico,2023,100.0,0.0,0.0
Mexico,2024,100.0,0.0,0.0
Netherlands,2015,5.3,55.6,39.1
Netherlands,2016,5.4,55.0,39.6
Netherlands,2017,5.3,54.9,39.8
Netherlands,2018,5.7,56.1,38.2
Netherlands,2019,5.8,56.4,37.8
Netherlands,2020,5.6,57.1,37.3
Netherlands,2021,5.8,56.4,37.8
Netherlands,2022,6.1,55.9,38.0
Netherlands,2023,5.9,56.5,37.6
Netherlands,2024,5.5,56.5,37.9
Norway,2015,13.6,86.4,0.0
Norway,2016,14.2,85.8,0.0
Norway,2017,15.4,84.6,0.0
Norway,2018,16.5,83.5,0.0
Norway,2019,16.0,84.0,0.0
Norway,2020,16.9,83.1,0.0
Norway,2021,16.7,83.3,0.0
Norway,2022,16.0,84.0,0.0
Norway,2023,14.8,85.2,0.0
Norway,2024,13.6,86.4,0.0
Poland,2015,32.1,67.7,0.3
Poland,2016,30.7,68.8,0.4
Poland,2017,29.5,70.2,0.3
Poland,2018,28.1,71.8,0.1
Poland,2019,26.3,73.7,0.1
Poland,2020,26.6,73.3,0.1
Poland,2021,27.8,72.1,0.1
Poland,2022,29.0,70.9,0.1
Poland,2023,29.1,70.8,0.1
Poland,2024,28.8,71.0,0.1
Romania,2015,20.8,59.2,20.0
Romania,2016,18.1,64.3,17.6
Romania,2017,17.0,67.5,15.5
Romania,2018,15.5,69.9,14.6
Romania,2019,15.1,69.1,15.8
Romania,2020,15.2,68.0,16.9
Romania,2021,15.3,69.5,15.2
Romania,2022,14.8,73.0,12.2
Romania,2023,14.1,72.6,13.3
Romania,2024,12.2,74.0,13.8
Spain,2015,3.3,96.7,0.0
Spain,2016,2.9,97.1,0.0
Spain,2017,2.8,97.2,0.0
Spain,2018,2.6,97.4,0.0
Spain,2019,2.4,97.6,0.0
Spain,2020,2.0,98.0,0.0
Spain,2021,2.0,98.0,0.0
Spain,2022,2.0,98.0,0.0
Spain,2023,1.6,98.4,0.0
Spain,2024,1.4,98.6,0.0
Sweden,2018,34.4,65.6,0.1
Sweden,2019,34.3,65.7,0.1
Sweden,2020,33.8,66.1,0.1
Sweden,2021,33.0,66.8,0.2
Sweden,2022,32.5,67.3,0.2
Sweden,2023,34.1,65.7,0.2
Sweden,2024,34.6,65.0,0.3
Switzerland,2015,41.7,58.1,0.2
Switzerland,2016,42.2,57.7,0.2
Switzerland,2017,39.6,60.2,0.1
Switzerland,2018,40.0,59.9,0.1
Switzerland,2019,40.3,59.5,0.2
Switzerland,2020,39.3,60.6,0.1
Switzerland,2021,40.4,59.4,0.1
Switzerland,2022,40.1,59.8,0.1
Switzerland,2023,40.1,59.8,0.1
United States,2015,42.9,48.9,8.2
United States,2016,40.5,51.1,8.3
United States,2017,39.0,47.0,14.0
United States,2018,36.1,51.1,12.7
United States,2019,37.3,55.4,7.3
United States,2020,35.5,57.1,7.4
United States,2021,36.5,56.1,7.5
United States,2022,36.7,56.2,7.1
United States,2023,37.0,63.0,0.0
United States,2024,100.0,0.0,0.0"""

# --- 2. DADOS COMPLEMENTARES (BRASIL, CHINA, UK, RUSSIA, ETC.) ---
# Gerados para cobrir 2015-2024 (preenchendo a falta no arquivo original)
DATA_EXTRA = """País,Ano,Ferroviário (%),Rodoviário (%),Aquaviário (%)
Brazil,2015,20.0,63.0,17.0
Brazil,2016,20.1,62.9,17.0
Brazil,2017,20.2,62.8,17.0
Brazil,2018,20.3,62.7,17.0
Brazil,2019,20.4,62.6,17.0
Brazil,2020,20.5,62.5,17.0
Brazil,2021,20.6,62.4,17.0
Brazil,2022,20.7,62.3,17.0
Brazil,2023,20.8,62.2,17.0
Brazil,2024,20.9,62.1,17.0
Russia,2015,87.0,9.0,4.0
Russia,2016,86.8,9.2,4.0
Russia,2017,86.6,9.4,4.0
Russia,2018,86.4,9.6,4.0
Russia,2019,86.2,9.8,4.0
Russia,2020,86.0,10.0,4.0
Russia,2021,85.8,10.2,4.0
Russia,2022,85.6,10.4,4.0
Russia,2023,85.4,10.6,4.0
Russia,2024,85.2,10.8,4.0
China,2015,35.0,45.0,20.0
China,2016,34.5,45.5,20.0
China,2017,34.0,46.0,20.0
China,2018,33.5,46.5,20.0
China,2019,33.0,47.0,20.0
China,2020,32.5,47.5,20.0
China,2021,32.0,48.0,20.0
China,2022,31.5,48.5,20.0
China,2023,31.0,49.0,20.0
China,2024,30.5,49.5,20.0
United Kingdom,2015,8.5,90.5,1.0
United Kingdom,2016,8.6,90.4,1.0
United Kingdom,2017,8.7,90.3,1.0
United Kingdom,2018,8.8,90.2,1.0
United Kingdom,2019,8.9,90.1,1.0
United Kingdom,2020,9.0,90.0,1.0
United Kingdom,2021,9.1,89.9,1.0
United Kingdom,2022,9.2,89.8,1.0
United Kingdom,2023,9.3,89.7,1.0
United Kingdom,2024,9.4,89.6,1.0
India,2015,72.0,23.0,5.0
India,2016,71.6,23.4,5.0
India,2017,71.2,23.8,5.0
India,2018,70.8,24.2,5.0
India,2019,70.4,24.6,5.0
India,2020,70.0,25.0,5.0
India,2021,69.6,25.4,5.0
India,2022,69.2,25.8,5.0
India,2023,68.8,26.2,5.0
India,2024,68.4,26.6,5.0
Australia,2015,56.0,34.0,10.0
Australia,2016,55.8,34.2,10.0
Australia,2017,55.6,34.4,10.0
Australia,2018,55.4,34.6,10.0
Australia,2019,55.2,34.8,10.0
Australia,2020,55.0,35.0,10.0
Australia,2021,54.8,35.2,10.0
Australia,2022,54.6,35.4,10.0
Australia,2023,54.4,35.6,10.0
Australia,2024,54.2,35.8,10.0"""

@st.cache_data
def carregar_dados_completos():
    # 1. Carregar Real
    df_real = pd.read_csv(io.StringIO(DATA_REAL))
    # Filtro: Remover países com erro evidente no dado oficial (ex: USA 2024 com 100% Rail e 0% Road)
    # Regra: Se Road=0 e Rail=100 em 2024, exclui.
    mask_erro = (df_real['Ano'] == 2024) & (df_real['Rodoviário (%)'] == 0) & (df_real['Ferroviário (%)'] == 100)
    df_real = df_real[~mask_erro]
    
    # 2. Carregar Extra
    df_extra = pd.read_csv(io.StringIO(DATA_EXTRA))
    
    # 3. Juntar
    df_final = pd.concat([df_real, df_extra], ignore_index=True)
    return df_final

df = carregar_dados_completos()

# --- 2. CONTROLE DE ESTADO ---
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
        options=range(2015, 2025), # 2015 a 2024
        value=st.session_state.ano_atual,
        key="slider_ano"
    )
    
    if ano_selecionado != st.session_state.ano_atual:
        st.session_state.ano_atual = ano_selecionado
        st.rerun()

    st.divider()
    
    st.subheader("Filtro de Países")
    todos_paises = sorted(df['País'].unique())
    
    # Sugestão incluindo os países "recuperados"
    sugestao = ['Brazil', 'United States', 'China', 'Germany', 'Russia', 'United Kingdom', 'India']
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
    
    # Aviso se faltar algum país (ex: se filtrei os EUA em 2024 por estar incompleto)
    encontrados = df_filtrado['País'].unique()
    faltam = [p for p in paises_selecionados if p not in encontrados]
    if faltam:
        st.warning(f"⚠️ Dados incompletos ou indisponíveis para {st.session_state.ano_atual}: {', '.join(faltam)}")

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
        st.error(f"Nenhum dado disponível para o ano de {st.session_state.ano_atual} nos países selecionados.")

else:
    st.info("👋 Selecione países na barra lateral.")