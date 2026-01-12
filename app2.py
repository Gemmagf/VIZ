# streamlit_app_final.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# =========================
# Configuració inicial
# =========================
st.set_page_config(page_title="Criminalitat a Suïssa (2010-2022)", layout="wide")
st.title("Criminalitat a Suïssa (2010–2022)")
st.markdown("""
Explora l'evolució de delictes a Suïssa, comparatives entre cantons i relació amb variables socioeconòmiques.
Filtra per cantó, any i tipus de delicte per obtenir informació detallada.
""")

# =========================
# Carregar dataset
# =========================
@st.cache_data
def load_data():
    df  = pd.read_csv("df_final.csv", sep=';', decimal='.', encoding='utf-8')

  # utilitza el teu fitxer
    return df

df = load_data()

# =========================
# Carregar dataset
# =========================
@st.cache_data
def load_data():
    df  = pd.read_csv("df_final_compressed.csv.gz", sep=';', decimal='.', encoding='utf-8', compression='gzip')

  # utilitza el teu fitxer
    return df

df = load_data()

# =========================
# Sidebar - filtres
# =========================
st.sidebar.header("Filtres")
selected_year = st.sidebar.slider("Any", int(df['Any'].min()), int(df['Any'].max()), (int(df['Any'].min()), int(df['Any'].max())))
selected_canton = st.sidebar.selectbox("Cantó", options=["Tots"] + sorted(df['Canto_norm'].unique()))
selected_offence = st.sidebar.multiselect("Tipus de delicte", options=df['Tipus_de_Delicte'].unique(), default=df['Tipus_de_Delicte'].unique())

# =========================
# Aplicar filtres
# =========================
df_filtered = df[df['Any'].between(selected_year[0], selected_year[1])]
if selected_canton != "Tots":
    df_filtered = df_filtered[df_filtered['Canto_norm'] == selected_canton]
df_filtered = df_filtered[df_filtered['Tipus_de_Delicte'].isin(selected_offence)]

# =========================
# Secció 1: KPI metrics
# =========================
st.subheader("Indicadors generals")
total_crimes = df_filtered['Nombre_de_Delictes'].sum()
avg_crime_rate = df_filtered['Taxa_Criminalitat_per_1000'].mean()
avg_resolution = df_filtered['Percentatge_Casos_Resolts'].mean()
col1, col2, col3 = st.columns(3)
col1.metric("Total de delictes", f"{int(total_crimes):,}")
col2.metric("Taxa de crim mitjana (per 1000 habitants)", f"{avg_crime_rate:.2f}")
col3.metric("Percentatge mitjà de casos resolts", f"{avg_resolution:.2f}%")

st.markdown("---")


# =========================
# Secció 2: Mapes per cantó
# =========================
st.subheader("Mapa de criminalitat per cantó")
map_data = df_filtered.groupby(['Canto_norm', 'Any']).agg({
    'Taxa_Criminalitat_per_1000': 'mean',
    'Nombre_de_Delictes': 'sum'
}).reset_index()

selected_metric = st.selectbox("Mètrica del mapa", ["Taxa_Criminalitat_per_1000", "Nombre_de_Delictes"])
map_fig = px.choropleth(
    map_data[map_data['Any'] == selected_year[1]],
    geojson=geojson,
    locations='Canto_norm',
    featureidkey="properties.name",
    color=selected_metric,
    color_continuous_scale="Reds",
    hover_name='Canto_norm',
    hover_data={selected_metric: True, 'Any': True},
    labels={selected_metric: "Crims" if selected_metric=="Nombre_de_Delictes" else "Crims per 1000 habitants"}
)
map_fig.update_geos(fitbounds="locations", visible=False)
map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(map_fig, use_container_width=True)

st.markdown("""

El mapa de criminalitat per cantó permet observar diferències territorials clares tant en la taxa de criminalitat per 1.000 habitants com en el nombre absolut de delictes. Els cantons urbans i densament poblats, com **Zuric, Vaud, Ginebra i Basel-Stadt**, destaquen de manera consistent amb valors més elevats, especialment quan s’analitza el nombre total de delictes. En canvi, cantons més petits i rurals com **Uri, Nidwalden, Obwalden o Glarus** presenten taxes i volums de criminalitat significativament inferiors al llarg de tot el període analitzat.

Quan es selecciona la taxa de criminalitat per 1.000 habitants, es posa de manifest que alguns cantons urbans, com **Ginebra i Basel-Stadt**, mantenen nivells estructuralment més alts fins i tot quan es corregeix per població, fet que suggereix una major intensitat del fenomen criminal associada a factors com la densitat, la mobilitat i l’activitat econòmica. En canvi, cantons amb població elevada però estructura més dispersa, com **Berna o St. Gallen**, mostren valors intermedis.

L’evolució temporal reflecteix una tendència general de descens de la criminalitat entre aproximadament 2012 i 2020 en la majoria de cantons, seguida d’un lleuger repunt en alguns casos a partir de 2021–2022. En conjunt, el mapa evidencia que la criminalitat a Suïssa presenta un fort component territorial i estructural, més relacionat amb el tipus de cantó (urbà vs. rural) que amb fluctuacions puntuals en el temps.
""")
# =========================
# Secció 3: Evolució temporal per cantó
# =========================
st.subheader("Evolució temporal dels delictes per cantó")
line_fig = px.line(
    map_data,
    x='Any',
    y=selected_metric,
    color='Canto_norm',
    markers=True,
    labels={"Canto_norm": "Cantó", selected_metric: "Crims" if selected_metric=="Nombre_de_Delictes" else "Crims per 1000 habitants"}
)
st.plotly_chart(line_fig, use_container_width=True)

st.markdown("""
El gràfic d’evolució temporal permet analitzar com ha variat la criminalitat a cada cantó entre 2010 i 2022, tant en termes de nombre absolut de delictes com de taxa per 1.000 habitants, segons la mètrica seleccionada. S’observa una tendència generalitzada de creixement fins aproximadament els anys 2011–2012, seguida d’un descens sostingut de la criminalitat en la majoria de cantons fins al període 2019–2020.

Els cantons urbans com **Zuric, Vaud, Ginebra i Basel-Stadt** presenten nivells clarament superiors al llarg de tot el període, amb una separació visual notable respecte a la resta de cantons, fet que indica que les diferències territorials són persistents en el temps i no fruit de fluctuacions puntuals. En particular, **Ginebra i Basel-Stadt** destaquen també quan s’analitza la taxa de criminalitat, mostrant una major intensitat relativa del fenomen criminal.

A partir de 2021–2022 es detecta un lleuger repunt de la criminalitat en diversos cantons, que trenca la tendència descendent observada en els anys anteriors. Tot i així, aquest increment no retorna als màxims del període inicial. En conjunt, el gràfic evidencia una evolució temporal relativament sincronitzada entre cantons, però amb nivells estructuralment diferents segons el tipus de territori, especialment entre cantons urbans i rurals.
""")

# =========================
# Secció 4: Relació amb variables socioeconòmiques
# =========================

st.subheader("Relació entre PIB, % d'estrangers i taxa de crim")

# 1️⃣ Treballem només amb "Total de casos" (una observació per cantó-any)
df_scatter = df_filtered[
    df_filtered['Nivell_de_Resolucio'] == 'Total de casos'
]

# 2️⃣ Agregació explícita (evita errors i és semànticament correcta)
scatter_data = (
    df_scatter
    .groupby(['Canto_norm', 'Any'], as_index=False)
    .agg(
        Taxa_Criminalitat_per_1000=('Taxa_Criminalitat_per_1000', 'mean'),
        PIB_per_Capita=('PIB_per_Capita', 'first'),
        Percentatge_Estrangers=('Percentatge_Estrangers', 'first'),
        Poblacio_Total=('Poblacio_Total', 'first')
    )
)

# 3️⃣ Scatter plot
scatter_fig = px.scatter(
    scatter_data,
    x='PIB_per_Capita',
    y='Taxa_Criminalitat_per_1000',
    size='Poblacio_Total',
    color='Percentatge_Estrangers',
    hover_name='Canto_norm',
    animation_frame='Any',   # 🔥 molt potent per storytelling
    size_max=50,
    labels={
        "PIB_per_Capita": "PIB per càpita (CHF)",
        "Taxa_Criminalitat_per_1000": "Crims per 1.000 habitants",
        "Percentatge_Estrangers": "% població estrangera",
        "Any": "Any"
    },
    color_continuous_scale='Viridis'
)

st.plotly_chart(scatter_fig, use_container_width=True)

st.markdown("""

El gràfic de dispersió interactiu permet analitzar la relació entre el PIB per càpita, el percentatge de població estrangera i la taxa de criminalitat als cantons suïssos al llarg del període 2010–2022. L’animació temporal mostra que, malgrat les variacions anuals, la posició relativa dels cantons es manté força estable, fet que indica l’existència de patrons estructurals persistents.

No s’observa una relació lineal clara entre el nivell de renda i la taxa de criminalitat. Cantons amb PIB per càpita elevat presenten comportaments heterogenis, amb taxes de criminalitat tant altes com moderades. Això suggereix que el nivell de desenvolupament econòmic, per si sol, no és un factor explicatiu suficient del fenomen criminal.

En canvi, el percentatge de població estrangera mostra una associació més consistent amb taxes de criminalitat més elevades, especialment en cantons urbans i densament poblats com **Ginebra, Basel-Stadt, Vaud i Zuric**. Tot i això, aquesta relació no s’ha d’interpretar com una causalitat directa, sinó com el reflex de factors estructurals associats a la urbanització, la densitat poblacional, la mobilitat internacional i la concentració d’activitat econòmica.

Finalment, la dimensió temporal reforça la idea que les diferències entre cantons són persistents al llarg del temps, amb canvis graduals però sense alteracions brusques en els patrons generals, fet que apunta a una estructura territorial de la criminalitat relativament estable a Suïssa.
""")

# =========================
# Secció 4: Resolució de casos
# =========================
st.subheader("Resolució de casos per tipus de delicte")
stacked_data = df_filtered.groupby(['Tipus_de_Delicte', 'Nivell_de_Resolucio'])['Nombre_de_Delictes'].sum().reset_index()

top_n = 20
top_delictes = (
    df_filtered.groupby('Tipus_de_Delicte')['Nombre_de_Delictes'].sum()
    .sort_values(ascending=False)
    .head(top_n)
    .index
)

def categoritza_delicte(d):
    if 'vol' in d.lower() or 'détournement' in d.lower() or 'dommages' in d.lower():
        return 'Vols / Détournements / Dommages'
    elif 'violence' in d.lower() or 'lésions' in d.lower() or 'meurtre' in d.lower():
        return 'Violence / Homicide'
    elif 'fraude' in d.lower() or 'escroquerie' in d.lower() or 'corruption' in d.lower():
        return 'Fraude / Corruption'
    elif 'sexuel' in d.lower() or 'inceste' in d.lower() or 'prostitution' in d.lower():
        return 'Infractions sexuelles'
    else:
        return 'Autres'

stacked_data['Categorie'] = stacked_data['Tipus_de_Delicte'].apply(categoritza_delicte)
stacked_data_cat = stacked_data.groupby(['Categorie', 'Nivell_de_Resolucio'])['Nombre_de_Delictes'].sum().reset_index()




stacked_data['Categorie'] = stacked_data['Tipus_de_Delicte'].apply(categoritza_delicte)

# Agrupem per categoria i nivell de resolució
stacked_data_cat = stacked_data.groupby(
    ['Categorie', 'Nivell_de_Resolucio']
)['Nombre_de_Delictes'].sum().reset_index()

# Calculem percentatge dins de cada categoria
stacked_data_cat['Percentatge'] = stacked_data_cat.groupby('Categorie')['Nombre_de_Delictes'].transform(lambda x: 100 * x / x.sum())


stacked_fig = px.bar(
    stacked_data_cat,
    x='Categorie',
    y='Percentatge',
    color='Nivell_de_Resolucio',
    text=stacked_data_cat['Percentatge'].apply(lambda x: f"{x:.1f}%"),
    labels={"Percentatge": "Percentatge de delictes (%)"}
)

stacked_fig.update_layout(
    barmode='stack',
    xaxis_tickangle=-45,
    yaxis=dict(ticksuffix="%")
)

st.plotly_chart(stacked_fig, use_container_width=True)

st.markdown("""
El gràfic de barres apilat mostra la distribució percentual dels delictes segons la seva categoria i el nivell de resolució. L’anàlisi destaca clarament com diferents tipus de delictes presenten perfils molt diferents pel que fa a resolució.

Els delictes classificats com a **Vols / Détournements / Dommages** representen gairebé la meitat del total dels casos (50%), amb una proporció elevada de casos no resolts (41,2%) i només un 8,8% resolts. Això indica que aquest tipus d’infraccions és abundant i sovint difícil de resoldre.

En canvi, els delictes de **Violence / Homicide** tenen una taxa de resolució molt alta (43%), tot i representar una fracció menor del total (50%). Això suggereix que, malgrat la gravetat i complexitat dels casos, el sistema policial i judicial és relativament eficaç en aquest tipus d’infraccions.

Els delictes de **Fraude / Corruption** mostren una resolució parcial (aproximadament 28% resolts) i representen una proporció moderada del total (50%), indicant un cert grau d’èxit en la investigació però també dificultats inherents a la naturalesa oculta d’aquests delictes.

Les **Infractions sexuelles** tenen un perfil similar: tot i representar només una petita fracció del total, la proporció de casos resolts és superior al 41%, destacant l’atenció que reben aquests casos en la investigació.

Finalment, els delictes classificats com a **Autres** constitueixen un volum molt elevat (50% del total) amb un 31% de casos no resolts i 19% resolts, reflectint la diversitat i complexitat d’altres tipus d’infraccions menys categorizables.

En conjunt, el gràfic evidencia que la **resolució dels delictes depèn fortament de la categoria**, amb delictes més greus o específics mostrant majors taxes de resolució, mentre que delictes més comuns o generalistes sovint queden sense resoldre. Aquesta anàlisi permet identificar àrees on caldria reforçar la prevenció i els recursos d’investigació per millorar l’eficàcia global del sistema penal.
""")

# =========================
# Secció 5: Evolució temporal per categoria de delicte
# =========================
st.subheader("Evolució temporal per categoria de delicte (2010–2022)")

def categoritza_delicte(d):
    d_lower = d.lower()
    if 'vol' in d_lower or 'détournement' in d_lower or 'dommages' in d_lower:
        return 'Robatoris / Détournements / Danys'  # Vols / Détournements / Dommages
    elif 'violence' in d_lower or 'lésions' in d_lower or 'meurtre' in d_lower:
        return 'Violència / Homicidi'  # Violence / Homicide
    elif 'fraude' in d_lower or 'escroquerie' in d_lower or 'corruption' in d_lower:
        return 'Frau / Corrupció'  # Fraude / Corruption
    elif 'sexuel' in d_lower or 'inceste' in d_lower or 'prostitution' in d_lower:
        return 'Infraccions sexuals'  # Infractions sexuelles
    else:
        return 'Altres'  # Autres


df_filtered['Categorie'] = df_filtered['Tipus_de_Delicte'].apply(categoritza_delicte)

temporal_data = df_filtered.groupby(['Any', 'Categorie'])['Nombre_de_Delictes'].sum().reset_index()
line_cat_fig = px.line(
    temporal_data,
    x='Any',
    y='Nombre_de_Delictes',
    color='Categorie',
    markers=True,
    labels={"Nombre_de_Delictes": "Nombre de delictes"}
)
st.plotly_chart(line_cat_fig, use_container_width=True)

st.markdown("""
El gràfic de línies mostra l'evolució anual del **nombre de delictes a Suïssa entre 2010 i 2022**, segons les principals categories.

Alguns punts clau de la interpretació:

- **Altres**: Aquesta categoria inclou delictes menors i no específics. Tot i ser la més abundant (aproximadament 3,7–5,2 milions anuals), mostra **fluctuacions importants**: màxim el 2012, disminució constant fins al 2021 i un lleuger repunt el 2022. La volatilitat reflecteix la diversitat d’infraccions incloses en aquesta categoria.

- **Robatoris / Détournements / Danys**: Amb més d’un milió de casos anuals, representa la segona categoria més freqüent. Es detecta una **tendència a la baixa a partir del 2016**, indicant possibles efectes de mesures de prevenció i control en aquests tipus de delictes comuns.

- **Violència / Homicidi**: Tot i ser relativament poc nombrosos (≈45.000–50.000 casos anuals), els valors es mantenen **estables al llarg dels anys**, mostrant que els crims més greus i específics tenen un patró constant que requereix estratègies especialitzades de prevenció.

- **Frau / Corrupció**: Mostra un **augment progressiu** des de 38.000 casos el 2010 fins a quasi 96.000 el 2022. Aquest increment pot reflectir tant un augment real dels delictes com una millor detecció i denúncia, indicant la complexitat d’aquest tipus d’infraccions.

- **Infraccions sexuals**: La tendència és **relativament constant**, amb valors entre 42.000 i 54.000 casos anuals i un lleuger augment a partir del 2015–2016, possiblement degut a un registre més sistemàtic i major atenció a aquests casos.


Podem dir dons que les categories de delictes més abundants tendeixen a **disminuir amb el temps**, mentre que les menys nombroses o més complexes mostren **estabilitat o increment**. La **distribució desigual i les diferents tendències per categoria** indiquen que cal aplicar estratègies de prevenció diferenciades segons la naturalesa i la gravetat dels delictes. Aquesta anàlisi permet avaluar on **reforçar recursos de prevenció i investigació**, prioritzant tant delictes abundants com aquells que, tot i ser menys nombrosos, tenen un impacte social més rellevant.
""")

# =========================
# Secció 7: Evolució temporal de la resolució per categoria
# =========================
st.subheader("Taxa de resolució per categoria al llarg dels anys")

resolution_data = df_filtered[df_filtered['Nivell_de_Resolucio'] != 'Total de casos']
resolution_pct = resolution_data.groupby(['Any','Categorie','Nivell_de_Resolucio'])['Nombre_de_Delictes'].sum().reset_index()
resolution_pct['Percentatge'] = resolution_pct.groupby(['Any','Categorie'])['Nombre_de_Delictes'].transform(lambda x: 100*x/x.sum())

line_res_fig = px.line(
    resolution_pct[resolution_pct['Nivell_de_Resolucio']=='Resolts'],
    x='Any',
    y='Percentatge',
    color='Categorie',
    markers=True,
    labels={"Percentatge": "% casos resolts"}
)
st.plotly_chart(line_res_fig, use_container_width=True)

st.markdown("""
El gràfic d’evolució temporal mostra com ha variat la **taxa de resolució dels delictes a Suïssa** entre 2010 i 2022 segons les categories principals, complementant la informació sobre el nombre total de casos.

Alguns punts clau:

- **Robatoris / Détournements / Danys**: Tot i ser una de les categories més abundants (més d’un milió de casos anuals), presenten una **taxa de resolució relativament baixa** (≈15–22%). Aquest patró indica que aquests delictes són difícils de resoldre i requereixen mesures d’investigació específiques i reforçades.

- **Violència / Homicidi**: Aquesta categoria, amb un volum menor de casos (≈45.000–50.000 anuals), mostra una **taxa de resolució molt alta** (≈82–88%) al llarg de tot el període. Això reflecteix l’eficàcia del sistema judicial i policial davant dels delictes més greus i específics, que, malgrat la seva complexitat, són investigats de manera eficient.

- **Frau / Corrupció**: Tot i un **increment constant en el nombre de casos** des de 38.000 el 2010 fins a gairebé 96.000 el 2022, la taxa de resolució ha anat **disminuint progressivament del 80% al 41%**, indicant que aquests delictes, tot i ser detectats amb més freqüència, continuen sent difícils de resoldre completament per la seva naturalesa complexa i oculta.

- **Infraccions sexuals**: Manté una evolució **relativament estable** (≈42.000–54.000 casos anuals), amb una **alta taxa de resolució** (≈78–84%), demostrant que aquests delictes reben una atenció constant i que les investigacions són efectives.

- **Altres**: Categoria molt variada i abundant (≈3,7–5,2 milions de casos anuals), amb un comportament oscil·lant: màxim el 2012, disminució fins al 2021 i repunt lleuger el 2022. La taxa de resolució és **moderada** (≈32–44%), reflectint la dificultat d’investigar infraccions menors o menys categorizables.

**Conclusió general:**
- La **resolució dels delictes depèn fortament de la categoria**, amb delictes greus i específics mostrant taxes altes, mentre que els delictes més abundants i generals tendeixen a tenir una resolució baixa.
- Aquest patró evidencia la necessitat de **estratègies diferenciades**: reforçar els recursos d’investigació en delictes abundants difícils de resoldre, mentre es manté l’eficiència en la resolució de delictes greus.
- En conjunt, la combinació de dades de nombre de casos i taxa de resolució ofereix una **visió completa sobre la situació criminal** i les àrees prioritàries per a la prevenció i l’acció policial.
""")



# =========================
# Secció 8: Diferències entre cantons per categoria
# =========================
st.subheader("Distribució de delictes per cantó i categoria")
cantons_cat = df_filtered[df_filtered['Canto_norm'] != 'Switzerland'] \
    .groupby(['Canto_norm', 'Categorie'])['Nombre_de_Delictes'].sum().reset_index()
bar_canton_fig = px.bar(
    cantons_cat,
    x='Canto_norm',
    y='Nombre_de_Delictes',
    color='Categorie',
    text='Nombre_de_Delictes'
)
bar_canton_fig.update_layout(barmode='stack', xaxis_tickangle=-45)
st.plotly_chart(bar_canton_fig, use_container_width=True)
st.markdown("""
El gràfic de barres apilat mostra com es distribueixen els delictes entre els diferents cantons segons la seva categoria.

S’observa que els cantons més grans i urbans com **Zuric, Vaud, Ginebra i Bern** presenten el nombre absolut més elevat de delictes, amb especial concentració en la categoria de **Robatoris / Détournements / Danys** i **Altres**. Això reflecteix tant la major població com la concentració d’activitat econòmica i social en aquests territoris.

Els cantons més petits i rurals, com **Uri, Glarus o Nidwalden**, mostren un volum molt menor de delictes en totes les categories, destacant la influència de la dimensió poblacional i de la densitat urbana en la incidència criminal.

Pel que fa a les categories específiques, **Violència / Homicidi** i **Infraccions sexuals** mantenen valors més baixos en tots els cantons, indicant que aquests delictes, tot i la gravetat, són menys freqüents. **Frau / Corrupció** és moderada en tots els cantons, amb punts més destacats en zones amb activitat econòmica significativa.

En conjunt, el gràfic evidencia que hi ha **diferències clares entre cantons** pel que fa al tipus i nombre de delictes, amb factors com la població, urbanització i activitat econòmica com a principals determinants dels volums observats.
""")
# =========================
# Secció 9: Correlació socioeconòmica
# =========================
st.subheader("Correlació entre característiques socioeconòmiques i delictes")
corr_df = df_filtered.groupby('Canto_norm').agg({
    'Nombre_de_Delictes':'sum',
    'PIB_per_Capita':'mean',
    'Percentatge_Estrangers':'mean',
    'Poblacio_Total':'mean'
}).corr()
# Convertim a format apt per a heatmap
corr_matrix = corr_df.reset_index().melt(id_vars='index')
corr_matrix.columns = ['Variable1', 'Variable2', 'Correlacio']

# Creem el heatmap
heatmap_fig = px.imshow(
    corr_df,
    text_auto=True,
    color_continuous_scale='RdBu_r',
    zmin=-1, zmax=1,
    labels=dict(x="Variable", y="Variable", color="Correlació"),
)

# Mostrem al Streamlit amb un key únic
st.plotly_chart(heatmap_fig, use_container_width=True, key="heatmap_corr")
st.markdown("""
El heatmap de correlació mostra la relació estadística entre el nombre total de delictes per cantó i diverses variables socioeconòmiques i demogràfiques, com el **PIB per càpita**, el **percentatge d’estrangers** i la **població total**.

Alguns punts clau de la interpretació:

- **Nombre_de_Delictes vs. Població_Total (0.997)**: La correlació és molt alta i positiva, indicant que el nombre total de delictes està fortament determinat per la mida de la població del cantó. Cantons més grans, com **Zuric, Bern o Vaud**, presenten un volum molt superior de delictes simplement per la major població.

- **Nombre_de_Delictes vs. PIB_per_Capita (0.041)**: La correlació és pràcticament nul·la, la qual cosa suggereix que el nivell de renda per càpita no té un efecte directe sobre el nombre total de delictes. Això indica que el fenomen criminal no depèn principalment de la riquesa mitjana del cantó.

- **Nombre_de_Delictes vs. Percentatge_Estrangers (0.151)**: La correlació és lleugerament positiva, però baixa. Això reflecteix una tendència subtil: cantons amb més població estrangera poden registrar una incidència lleugerament més alta de delictes, però la relació no és forta i no implica causalitat directa. Altres factors com la densitat urbana, l’activitat econòmica i la mobilitat poden influir més.

- **PIB_per_Capita vs. Percentatge_Estrangers (0.604)**: Hi ha una correlació moderada positiva, indicant que cantons més rics solen tenir una proporció més alta de població estrangera. Això pot reflectir l’atracció de treballadors i professionals internacionals cap a zones urbanes i econòmicament actives.

En conjunt, el heatmap evidencia que **la variable que més explica el nombre total de delictes és la població del cantó**, mentre que factors com el PIB per càpita i el percentatge d’estrangers tenen un efecte molt més moderat. Aquesta informació és útil per ajustar les polítiques de prevenció i recursos policials segons la dimensió i característiques del cantó.
""")

# =========================
# Secció 10: Impacte de característiques socioeconòmiques en tendències per categoria
# =========================
st.subheader("Impacte de característiques socioeconòmiques en tendències de delictes per categoria")
bubble_data = df_filtered.groupby(['Any','Categorie','Canto_norm']).agg({
    'Nombre_de_Delictes':'sum',
    'PIB_per_Capita':'first',
    'Percentatge_Estrangers':'first',
    'Poblacio_Total':'first'
}).reset_index()

bubble_fig = px.scatter(
    bubble_data,
    x='PIB_per_Capita',
    y='Nombre_de_Delictes',
    size='Poblacio_Total',
    color='Percentatge_Estrangers',
    animation_frame='Any',
    hover_name='Canto_norm',
    facet_col='Categorie',
    size_max=40,
    color_continuous_scale='Viridis',
    labels={'Nombre_de_Delictes':'Delictes','Percentatge_Estrangers':'% estrangers','PIB_per_Capita':'PIB per càpita'}
)
st.plotly_chart(bubble_fig, use_container_width=True)

st.markdown("""
El gràfic de bombolles interactiu mostra la relació entre el nombre de delictes per categoria, el **PIB per càpita**, el **percentatge d’estrangers** i la **població total** dels cantons suïssos al llarg dels anys 2020–2022. Cada bombolla representa un cantó en un any determinat, la mida indica la població total i el color el percentatge d’estrangers.

Alguns punts clau de la interpretació:

- **Nombre de delictes vs. Població_Total**: Els cantons més poblats, com **Zuric, Bern o Vaud**, mostren les bombolles més grans i el volum més alt de delictes en categories comunes com **Altres** i **Robatoris / Détournements / Danys**. Això confirma que la dimensió de la població és el factor principal que determina el nombre absolut de delictes.

- **Nombre de delictes vs. PIB_per_Capita**: No s’observa una relació lineal clara. Tot i que alguns cantons amb PIB alt mostren volums elevats en categories com robatoris, altres cantons rics tenen menys delictes. Això suggereix que la riquesa mitjana no és un factor determinant per si sola en el volum de delictes.

- **Nombre de delictes vs. Percentatge_Estrangers**: Els cantons amb un percentatge més alt de població estrangera tendeixen a tenir bombolles més fosques, indicant més delictes en categories comunes. La relació és més visible en **Robatoris / Détournements / Danys** i **Altres**, mentre que delictes greus com **Violència / Homicidi** i **Infraccions sexuals** no mostren una associació clara.

- **Variació temporal (2020–2022)**: La posició relativa de les bombolles canvia lleugerament d’un any a un altre, però els patrons generals es mantenen constants. Els delictes comuns dominen el volum total, mentre que els delictes greus mantenen xifres relativament estables. Això reflecteix tendències estructurals persistents per cantó i categoria, amb canvis anuals moderats.

El gràfic evidencia que **la població del cantó és el factor que més determina el nombre de delictes**, mentre que el PIB per càpita i el percentatge d’estrangers tenen un efecte més moderat i específic per categoria. Aquesta informació ajuda a entendre millor quins factors socioeconòmics i demogràfics poden influir en les tendències criminals i permet orientar les polítiques preventives segons les característiques regionals.
""")
