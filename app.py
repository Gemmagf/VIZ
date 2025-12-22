# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ========================
# CONFIGURACIÓ PÀGINA
# ========================
st.set_page_config(page_title="Anàlisi de Reserves Hoteleres a Portugal", page_icon="🏨")
                   
st.title("Anàlisi de Reserves Hoteleres a Portugal")
st.markdown("""
Anàlisi de més de 100.000 reserves d'hotels urbans i resorts a Portugal, incloent cancel·lacions, tarifa mitjana per habitació, tipologies d'estada, segments de mercat i canals de distribució.  
Objectiu: proporcionar insights accionables per optimitzar rendibilitat, experiència dels clients i fidelització.
""")

# ========================
# CARREGAR DADES
# ========================
df = pd.read_csv("hotel_bookings.csv")

# ========================
# NETEJA DE NOMS DE COLUMNES I CATEGORIES
# ========================
df.rename(columns={
    'hotel':'Tipus_Hotel',
    'is_canceled':'Cancel·lada',
    'lead_time':'Dies_Abans',
    'adr':'Tarifa',
    'adults':'Adults',
    'children':'Nens',
    'distribution_channel':'Canal',
    'market_segment':'Segment_Mercat',
    'trip_type':'Tipus_Viatge',
    'arrival_date_month':'Mes'
}, inplace=True)

df['Tipus_Hotel'] = df['Tipus_Hotel'].map({'Resort Hotel':'Resort','City Hotel':'Hotel Ciutat'})
df['Cancel·lada'] = df['Cancel·lada'].map({0:'Check-Out',1:'Cancel·lada'})
df['Segment_Mercat'] = df['Segment_Mercat'].replace('undefined', np.nan)
df = df[df['Segment_Mercat'].notna()]
df = df[df['Canal'].notna()]

# ========================
# PALETA DE COLORS
# ========================
PALETTE = ["#c4002d", "#ffd231", "#2d733c", "#306fbe", "#c78095", "#b34667"]

# ========================
# SECCIÓ 1: KPIs
# ========================
st.subheader("Indicadors Clau Generals")
cancel_rate = round(df['Cancel·lada'].eq('Cancel·lada').mean()*100,1)
avg_tarifa = round(df['Tarifa'].mean(),2)
avg_stay = round(df[['stays_in_week_nights','stays_in_weekend_nights']].sum(axis=1).mean(),1)
rev_par = round(avg_tarifa * (1 - cancel_rate/100),2)

kpi_cols = st.columns(4)
kpi_cols[0].metric("Cancel·lacions (%)", f"{cancel_rate}%")
kpi_cols[1].metric("Tarifa Mitjana per Habitació (€)", f"{avg_tarifa}")
kpi_cols[2].metric("Dies Mitjana Estada", f"{avg_stay}")
kpi_cols[3].metric("Ingressos per Hab. Disponible (€)", f"{rev_par}")

st.caption(
    "Tot i un ADR (Tarifa Mitjana Diària per Habitació) aparentment sòlid, el RevPAR real es veu reduït de manera significativa "
    "per l'impacte de les cancel·lacions. La gestió del risc de cancel·lació és clau per protegir ingressos."
)


st.markdown("---")

# ========================
# SECCIÓ 2: Visió General de Cancel·lacions per Tipus d'Hotel (Side-by-Side)
# ========================
st.subheader("Visió General de Cancel·lacions per Tipus d'Hotel")

tipus_hotels = df['Tipus_Hotel'].unique()
cols = st.columns(len(tipus_hotels))

for i, hotel in enumerate(tipus_hotels):
    df_hotel = df[df['Tipus_Hotel'] == hotel]
    df_counts = df_hotel['Cancel·lada'].value_counts().reset_index()
    df_counts.columns = ['Cancel·lada','Nombre']

    pie = px.pie(
        df_counts,
        names='Cancel·lada',
        values='Nombre',
        color='Cancel·lada',
        color_discrete_sequence=["#2d733c", "#c78095"],
        hole=0.3
    )
    pie.update_traces(textinfo='percent+label', textfont_size=14)
    pie.update_layout(
        title=f"{hotel}",
        showlegend=True,
        margin=dict(t=40, b=0, l=0, r=0)
    )
    cols[i].plotly_chart(pie, use_container_width=True)
st.caption(
    "Els hotels urbans mostren una proporció de cancel·lacions superior als resorts. "
    "Això reflecteix un client més flexible i sensible a canvis d'agenda, especialment en viatges curts o professionals."
)
st.markdown(
    "> Insight clau: els resorts tenen menys cancel·lacions, però cada cancel·lació acostuma a tenir un impacte econòmic més elevat."
)
st.markdown("---")

# ========================
# SECCIÓ 3: Cancel·lacions segons Tipus de Viatge
# ========================
st.subheader("Cancel·lacions segons Tipus de Viatge")
cancel_trip = df.groupby(['Tipus_Viatge','Cancel·lada']).size().reset_index(name='Nombre')
fig_trip = px.bar(
    cancel_trip,
    x='Tipus_Viatge',
    y='Nombre',
    color='Cancel·lada',
    color_discrete_sequence=PALETTE,
    text='Nombre'
)
fig_trip.update_layout(barmode='stack', legend_title_text="Estat reserva")
st.plotly_chart(fig_trip, use_container_width=True)
st.caption(
    "Els viatges no recreatius concentren una proporció elevada de cancel·lacions. "
    "Aquest patró és coherent amb viatges corporatius o funcionals, més exposats a canvis d'última hora."
)
st.markdown(
    "> Implicació: el tipus de viatge és un predictor més fort de cancel·lació que el preu."
)
st.markdown("---")

# ========================
# SECCIÓ 4: Segments de Mercat per Tipus d'Hotel
# ========================
st.subheader("Segments de Mercat per Tipus d'Hotel")
seg_summary = df.groupby(['Segment_Mercat','Tipus_Hotel']).size().reset_index(name='Nombre')
fig_seg = px.bar(
    seg_summary,
    x='Segment_Mercat',
    y='Nombre',
    color='Tipus_Hotel',
    color_discrete_sequence=["#2d733c", "#306fbe"],
    text='Nombre'
)
fig_seg.update_layout(barmode='group', legend_title_text="Tipus d'Hotel")
st.plotly_chart(fig_seg, use_container_width=True)


st.caption(
    "Els hotels urbans depenen més de canals intermediats, mentre que els resorts mostren "
    "més pes del segment directe i d'oci."
)
st.markdown(
    "> Insight estratègic: una major dependència d'una Agència de Viatges Online implica més volatilitat i més risc de cancel·lació."
)
st.markdown("---")



# ========================
# SECCIÓ 5: Tendències Estacionals
# ========================
st.subheader("Tendències Estacionals")
month_order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
month_summary = df.groupby(['Mes','Tipus_Hotel'])['Tarifa'].mean().reset_index()
month_summary['Mes'] = pd.Categorical(month_summary['Mes'], categories=month_order, ordered=True)
month_summary = month_summary.sort_values('Mes')

fig_area = px.area(
    month_summary,
    x='Mes',
    y='Tarifa',
    color='Tipus_Hotel',
    line_group='Tipus_Hotel',
    color_discrete_sequence=["#2d733c", "#306fbe"],
    labels={'Mes':'Mes','Tarifa':'Tarifa Mitjana (€)','Tipus_Hotel':'Tipus d\'Hotel'}
)
st.plotly_chart(fig_area, use_container_width=True)

st.caption(
    "Els resorts presenten una estacionalitat molt marcada, amb pics de tarifa a l'estiu. "
    "Els hotels urbans mostren una evolució més estable durant l'any."
)
st.markdown(
    "> Quan la tarifa és més alta, el cost potencial d'una cancel·lació també augmenta."
)
st.markdown("---")

# ========================
# SECCIÓ 6: Temps d'Antelació de Reserva vs ADR
# ========================
st.subheader("Temps d'Antelació de Reserva vs Tarifa Mitjana per Habitació")
fig_scatter_tarifa = px.scatter(
    df,
    x='Dies_Abans',
    y='Tarifa',
    size='Tarifa',
    size_max=30,
    color='Tipus_Hotel',
    hover_data=['Segment_Mercat','Cancel·lada'],
    labels={'Dies_Abans':'Dies abans de l\'arribada','Tarifa':'Tarifa (€)'}
)
st.plotly_chart(fig_scatter_tarifa, use_container_width=True, key='scatter_tarifa')

st.caption(
    "No s'observa una relació lineal clara entre antelació i tarifa. "
    "Reserves fetes amb molta anticipació poden tenir ADR elevat però també major risc de cancel·lació."
)
st.markdown(
    "> Reservar aviat no implica necessàriament més compromís del client."
)
st.markdown("---")


# ========================
# SECCIÓ 4: Cancel·lacions segons Antelació de Reserva (Scatter pèrdua econòmica)
# ========================
# ========================
# SECCIÓ: Cancel·lacions segons Antelació de Reserva (Pèrdua Econòmica)
# ========================
st.subheader("Cancel·lacions segons Antelació de Reserva i Pèrdua Econòmica")

df_cancelled = df[df['Cancel·lada'] == 'Cancel·lada'].copy()

df_cancelled['Dies_Abans_Cat'] = pd.cut(
    df_cancelled['Dies_Abans'],
    bins=[0, 7, 14, 30, 60, 90, 180, 365],
    labels=["0–7", "8–14", "15–30", "31–60", "61–90", "91–180", "181–365"]
)

cancel_agg = (
    df_cancelled
    .groupby(['Dies_Abans_Cat', 'Tipus_Hotel'])
    .agg(
        Nombre=('Cancel·lada', 'count'),
        Perdua=('Tarifa', 'sum')
    )
    .reset_index()
)

fig_cancel_scatter = px.scatter(
    cancel_agg,
    x='Dies_Abans_Cat',
    y='Nombre',
    size='Nombre',
    color='Perdua',
    facet_col='Tipus_Hotel',
    size_max=55,
    color_continuous_scale='Greens',
    labels={
        'Dies_Abans_Cat': "Dies abans de l'arribada",
        'Nombre': "Nombre de cancel·lacions",
        'Perdua': "Pèrdua econòmica (€)",
        'Tipus_Hotel': "Tipus d'hotel"
    }
)

fig_cancel_scatter.update_layout(
    coloraxis_colorbar=dict(title="Pèrdua (€)"),
    yaxis_title="Nombre de cancel·lacions",
    xaxis_title="Antelació de la reserva",
    margin=dict(t=40)
)

st.plotly_chart(fig_cancel_scatter, use_container_width=True, key="cancel_scatter_loss")

st.caption(
    "El color indica la pèrdua econòmica acumulada per cancel·lacions, "
    "mentre que la mida del punt representa el volum de cancel·lacions. "
    "Insight: permet identificar en quin tipus d’hotel i amb quina antelació "
    "les cancel·lacions són més costoses."
)
st.caption(
    "El color indica la pèrdua econòmica acumulada i la mida el volum de cancel·lacions. "
    "Les cancel·lacions amb molta antelació, especialment en hotels  de ciutat, concentren les pèrdues més elevades."
)
st.markdown(
    "> Insight crític: el risc econòmic no es concentra en el last-minute, sinó en reserves anticipades d'alt valor."
)


st.markdown("---")



# ========================
# SECCIÓ 7: Distribució d'Adults i Nens (Treemap)
# ========================
st.subheader("Distribució d'Adults i Nens")
family_summary = df.groupby(['Adults','Nens']).size().reset_index(name='Nombre')
family_summary['Tipus_Familia'] = family_summary['Adults'].astype(str)+' adults & '+family_summary['Nens'].astype(str)+' nens'
fig_family = px.treemap(
    family_summary,
    path=['Tipus_Familia'],
    values='Nombre',
    color='Nombre',
    color_continuous_scale='Teal'
)
st.plotly_chart(fig_family, use_container_width=True)
st.caption(
    "La majoria de reserves corresponen a parelles i famílies petites, perfils associats a estades més llargues."
)
st.markdown(
    "> Quan aquests clients cancel·len, la pèrdua econòmica és proporcionalment més elevada."
)
st.markdown("---")

# ========================
# SECCIÓ 8: Tarifa Mitjana per Habitació segons Canal
# ========================
st.subheader("Tarifa Mitjana per Habitació segons Canal de Distribució")
dist_summary = df.groupby('Canal')['Tarifa'].mean().reset_index()
dist_summary['Tarifa'] = dist_summary['Tarifa'].round(2)

fig_dist = px.bar(
    dist_summary,
    x='Canal',
    y='Tarifa',
    text=dist_summary['Tarifa'].apply(lambda x: f"{x}€"),
    color='Canal',
    color_discrete_sequence=PALETTE
)
fig_dist.update_traces(showlegend=False)
fig_dist.update_layout(yaxis_title="Tarifa Mitjana (€)", xaxis_title="Canal")
st.plotly_chart(fig_dist, use_container_width=True)
st.caption(
    "Els canals directes i corporatius mostren una tarifa mitjana inferior i més estable."
)
st.markdown(
    "> Estratègia clau: potenciar el canal directe millora marge i redueix dependència d'intermediaris."
)
st.markdown("---")
# ========================
# SECCIÓ 10: Durada Mitja Estada per Tipus d'Hotel i Segment
# ========================
st.subheader("Durada Mitja d'Estada")
df['Durada_Estada'] = df['stays_in_week_nights'] + df['stays_in_weekend_nights']
stay_summary = df.groupby(['Tipus_Hotel','Segment_Mercat'])['Durada_Estada'].mean().reset_index()
fig_stay = px.bar(
    stay_summary,
    x='Segment_Mercat',
    y='Durada_Estada',
    color='Tipus_Hotel',
    color_discrete_sequence=["#2d733c", "#306fbe"],
    text=stay_summary['Durada_Estada'].round(1)
)
fig_stay.update_layout(barmode='group', yaxis_title="Dies mitjans d'estada")
st.plotly_chart(fig_stay, use_container_width=True, key='stay')

st.caption(
    "Els resorts presenten estades més llargues, mentre que els hotels urbans concentren estades curtes."
)
st.markdown(
    "> Estades llargues + ADR alt + cancel·lació = màxim impacte negatiu sobre ingressos."
)
