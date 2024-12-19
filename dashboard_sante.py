import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


@st.cache_data
def load_data():
    fichier = "effectifs.csv"
    df = pd.read_csv(fichier, sep=';', on_bad_lines='skip')
    
    df['annee'] = pd.to_numeric(df['annee'], errors='coerce') 
    df = df[(df['annee'] >= 2015) & (df['annee'] <= 2022)]
    
    return df

df = load_data()


st.header(f"Analyse graphique des Pathologies psychiatriques: effectif de patients par pathologie, sexe, classe d'âge et territoire")

# Premier graphique : Nombre total de personnes prises en charge par l'assurance maladie


years = sorted(df['annee'].unique()) 
selected_year = st.selectbox("Sélectionner une année pour filtrer les données :", options=years, key="year_filter")

filtered_df = df[df['annee'] == selected_year] 

patho_psy = ['Maladies psychiatriques']
patho_cardio = ['Maladies cardioneurovasculaires']

psy_total = filtered_df[filtered_df['patho_niv1'].isin(patho_psy)]['Ntop'].sum()
cardio_total = filtered_df[filtered_df['patho_niv1'].isin(patho_cardio)]['Ntop'].sum()

st.subheader(f'Total des personnes prises en charge pour chaque pathologie ({selected_year}):')
st.write(f"Total pour Maladies psychiatriques : {psy_total}")
st.write(f"Total pour Maladies cardioneurovasculaires : {cardio_total}")

totals = [psy_total, cardio_total]
categories = ['Maladies psychiatriques', 'Maladies cardioneurovasculaires']

def millions_formatter(x, _):
    return f'{x / 1e6:.1f}M'

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(categories, totals, color=['skyblue', 'lightcoral'])
ax.set_title(f'Personnes prises en charge par Pathologie ({selected_year})', fontsize=14)
ax.set_xlabel('Pathologies', fontsize=10)
ax.set_ylabel('Nombre de personnes prises en charge (en millions)', fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))  
ax.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)





# Deuxième graphique : Graphique linéaire pour les personnes prises en charge par année pour chaque pathologie

psy_par_annee = df[df['patho_niv1'].isin(patho_psy)].groupby('annee')['Ntop'].sum()
cardio_par_annee = df[df['patho_niv1'].isin(patho_cardio)].groupby('annee')['Ntop'].sum()

comparaison = pd.DataFrame({
    'total maladies psychiatriques': psy_par_annee,
    'total maladies cardioneurovasculaires': cardio_par_annee
}).fillna(0)

def millions_formatter(x, _):
    return f'{x / 1e6:.1f}M'

fig2, ax2 = plt.subplots(figsize=(7, 5))  
ax2.plot(comparaison.index, comparaison['total maladies psychiatriques'], marker='o', label='Maladies psychiatriques', color='skyblue')
ax2.plot(comparaison.index, comparaison['total maladies cardioneurovasculaires'], marker='o', label='Maladies cardioneurovasculaires', color='lightcoral')

ax2.set_title('Nombre de prises en charge par année (2015-2022)', fontsize=14)
ax2.set_xlabel('Année', fontsize=12)
ax2.set_ylabel('Nombre de prises en charge (en millions)', fontsize=12)
ax2.set_xticks(comparaison.index)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)

ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

st.pyplot(fig2)






# Troisième graphique : Graphique en barres pour les cas psychiatriques par groupe d'âge avec filtre par année

psy_df = df[df['patho_niv1'] == 'Maladies psychiatriques']

years = sorted(psy_df['annee'].unique())
selected_year = st.selectbox("Sélectionner une année :", years)

filtered_df = psy_df[psy_df['annee'] == selected_year]

cas_par_tranche = filtered_df[filtered_df['libelle_classe_age'] != 'tous âges'].groupby('libelle_classe_age')['Ntop'].sum()

cas_par_tranche = cas_par_tranche.sort_index()  
if 'de 5 à 9 ans' in cas_par_tranche.index:
    cas_par_tranche = (
        pd.concat([ 
            cas_par_tranche.iloc[:1],  
            cas_par_tranche.loc[['de 5 à 9 ans']],  
            cas_par_tranche.drop(index='de 5 à 9 ans').iloc[1:]  
        ])
    )

tranche_max = cas_par_tranche.idxmax() if not cas_par_tranche.empty else "N/A"
valeur_max = cas_par_tranche.max() if not cas_par_tranche.empty else 0

st.subheader(f"Cas psychiatriques par groupe d'âge pour l'année {selected_year}:")
if not cas_par_tranche.empty:
    st.write(f"Le groupe d'âge le plus touché est : {tranche_max} avec {valeur_max} cas.")
else:
    st.write("Aucune donnée disponible pour l'année sélectionnée.")

def millions_formatter(x, _):
    return f'{x / 1e6:.1f}M'

fig3, ax3 = plt.subplots(figsize=(7, 5))  
cas_par_tranche.plot(kind='bar', color='teal', ax=ax3)
ax3.set_title(f'Cas psychiatriques par groupe d\'âge ({selected_year})', fontsize=14)
ax3.set_xlabel('Groupe d\'âge', fontsize=12)
ax3.set_ylabel('Nombre de cas (en millions)', fontsize=12)
ax3.yaxis.set_major_formatter(FuncFormatter(millions_formatter))  
ax3.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig3)







# Quatrième graphique : Graphique en barres pour les cas psychiatriques par région

years = df['annee'].unique()  
selected_year = st.selectbox("Sélectionner une année pour filtrer les données :", options=sorted(years))

filtered_df = df[(df['patho_niv1'] == 'Maladies psychiatriques') & (df['annee'] == selected_year)]

cas_par_region = filtered_df[filtered_df['region'] != 99].groupby('region')['Ntop'].sum()
cas_par_region = cas_par_region.sort_values(ascending=False)

region_max = cas_par_region.idxmax() if not cas_par_region.empty else "N/A"
valeur_max_region = cas_par_region.max() if not cas_par_region.empty else 0

st.subheader("Cas psychiatriques par région :")
if not cas_par_region.empty:
    st.write(f"En {selected_year}, la région avec le plus grand nombre de cas est : {region_max} avec {valeur_max_region} cas.")
else:
    st.write(f"Aucune donnée disponible pour l'année sélectionnée : {selected_year}.")

def millions_formatter(x, _):
    return f'{x / 1e6:.1f}M'


fig4, ax4 = plt.subplots(figsize=(7, 5))  
cas_par_region.plot(kind='bar', color='purple', ax=ax4)
ax4.set_title(f'Cas psychiatriques par région ({selected_year})', fontsize=14)
ax4.set_xlabel('Région', fontsize=12)
ax4.set_ylabel('Nombre de cas (en millions)', fontsize=12)
ax4.yaxis.set_major_formatter(FuncFormatter(millions_formatter))  
ax4.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig4)





# Cinquième graphique : Évolution des cas psychiatriques de 2016 à 2022

psy_keywords = ['Maladies psychiatriques']

psy_par_annee = df[df['patho_niv1'].isin(psy_keywords)].groupby('annee')['Ntop'].sum()

psy_max = psy_par_annee.idxmax()
psy_min = psy_par_annee.idxmin()

st.subheader("Évolution des cas psychiatriques (2016-2022) :")
st.write(f"Année avec le plus grand nombre de cas psychiatriques : {psy_max} avec {psy_par_annee[psy_max]} cas.")
st.write(f"Année avec le moins de cas psychiatriques : {psy_min} avec {psy_par_annee[psy_min]} cas.")

def millions_formatter(x, _):
    return f'{x / 1e6:.1f}M'

fig5, ax5 = plt.subplots(figsize=(7, 5))  
ax5.plot(psy_par_annee.index, psy_par_annee.values, marker='o', linestyle='-', color='purple', label='Cas psychiatriques')

ax5.annotate(f'Max ({psy_par_annee[psy_max]})',
             xy=(psy_max, psy_par_annee[psy_max]),
             xytext=(psy_max, psy_par_annee[psy_max] + 300),
             arrowprops=dict(facecolor='black', arrowstyle='->'),
             fontsize=12)

ax5.annotate(f'Min ({psy_par_annee[psy_min]})',
             xy=(psy_min, psy_par_annee[psy_min]),
             xytext=(psy_min, psy_par_annee[psy_min] - 350),
             arrowprops=dict(facecolor='black', arrowstyle='->'),
             fontsize=12)

ax5.set_title("Évolution des cas psychiatriques (2016-2022)", fontsize=14)
ax5.set_xlabel("Année", fontsize=12)
ax5.set_ylabel("Nombre de cas", fontsize=12)
ax5.set_xticks(psy_par_annee.index)
ax5.set_xticklabels(psy_par_annee.index, rotation=45)
ax5.grid(axis='y', linestyle='--', alpha=0.7)
ax5.legend()

ax5.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

st.pyplot(fig5)





# Sixième graphique : Diagramme circulaire des cas psychiatriques par sexe

pathologie_cible = ['Maladies psychiatriques']
df_filtre = df[df['patho_niv1'].isin(pathologie_cible)]

cas_par_sexe = df_filtre[df_filtre['libelle_sexe'] != 'tous sexes'].groupby('libelle_sexe')['Ntop'].sum()

fig6, ax6 = plt.subplots(figsize=(7, 7)) 
explode = [0.1] * len(cas_par_sexe)
ax6.pie(cas_par_sexe, labels=cas_par_sexe.index, autopct='%1.1f%%',
        startangle=90, colors=['skyblue', 'lightcoral', 'chocolate'], explode=explode)
ax6.set_title('Prépondérance des cas psychiatriques par sexe', fontsize=14)
ax6.axis('equal')
st.pyplot(fig6)
