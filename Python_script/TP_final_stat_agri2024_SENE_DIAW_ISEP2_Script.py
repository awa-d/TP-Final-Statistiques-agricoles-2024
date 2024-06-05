'''______________________________________________________________________________________________

   T R A V A U X   P R A T I Q U E S   F I N A U X   D E   S T A T I S T I Q U E S   A G R I C O L E S 
   
                              E L E V A G E     P A S T O R A L E 
             __________________________________________________________________________
              
                  Rédigé par Awa DIAW et Malick SENE  élèves en ISEP 2 à l'ENSAE
               
'''

                                     ##Import libraries##
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf

                                     ##Import dataset##
data_emigration = pd.read_stata("emigration_cleaned.dta")
data_ventes = pd.read_stata("vente_betail_cleaned.dta")
data_ft = pd.read_stata("data_FT.dta")



'''
===================                                                              ===================

                                2.1 Préparation et nettoyage des données
                             
===================                                                              ===================
'''

'''
Nous avons exécuté un do-file de prétraitement des données. Ce fichier a permis d'importer les données brutes et 
d'explorer leur structure initiale. Ensuite, les doublons et les valeurs manquantes ont été traités pour la variable
ID. Des variables de localisation ont été générées à partir des ID, et les variables inutiles ont été supprimées
pour simplifier le jeu de données.
Pour les données de vente de bétail, le do-file a harmonisé et restructuré les données, en sélectionnant 
les variables pertinentes et en transformant les données pour faciliter l'analyse. Enfin, les données d'émigration
ont été nettoyées, les noms des destinations ont été standardisés et codés pour une analyse plus précise. 
Ces étapes ont transformé les données brutes en un format structuré et plus facile à manipuler.
'''

'''
===================                                                         ===================

                                2.2 Subsistance du ménage
                             
===================                                                         ===================
'''



'''_____________1. la proportion de familles pratiquant l’agriculture en plus de l’élevage______________'''

# 
proportions_agriculture_by_country = data_ft.groupby('country').apply(
    lambda x: (x['AGRICULTURE'] == 'Oui').mean()
).reset_index(name='Proportion Agriculture')

print(proportions_agriculture_by_country)


'''_____________2. La proportion pour les différentes cultures_______________________________________'''

# Liste des colonnes de cultures spécifiques
culture_columns = ['Mil', 'Sorgho', 'Maïs', 'Niébé', 'Manioc', 'Arachide', 'Coton', 'Culturesmaraîchères']

# Initialiser un DataFrame pour les résultats des proportions de cultures par pays
results = pd.DataFrame()

for country, group in data_ft.groupby('country'):
    # Filtrer les familles pratiquant l'agriculture
    agriculture_families = group[group['AGRICULTURE'] == 'Oui']

    # Calculer le nombre total de pratiques agricoles
    total_cultures_practiced = 0
    for culture in culture_columns:
        total_cultures_practiced += agriculture_families[agriculture_families[culture].isin(['Oui', culture])].shape[0]

    # Inclure les pratiques de la variable 'Autres'
    autres_modalities = agriculture_families['Autres'].unique()
    autres_modalities = [modality for modality in autres_modalities if modality not in ["Pas d'autres", 'Non', '']]
    for modality in autres_modalities:
        total_cultures_practiced += agriculture_families[agriculture_families['Autres'] == modality].shape[0]

    # Calculer les proportions pour chaque culture spécifique
    proportions_cultures = {}
    for culture in culture_columns:
        num_families_culture = agriculture_families[agriculture_families[culture].isin(['Oui', culture])].shape[0]
        proportions_cultures[culture] = num_families_culture / total_cultures_practiced

    # Calculer les proportions pour les différentes cultures dans 'Autres'
    for modality in autres_modalities:
        num_families_autres = agriculture_families[agriculture_families['Autres'] == modality].shape[0]
        proportions_cultures[modality] = num_families_autres / total_cultures_practiced

    # Créer un DataFrame temporaire pour les résultats de chaque pays
    temp_results = pd.DataFrame(list(proportions_cultures.items()), columns=['Culture', 'Proportion'])
    temp_results['Country'] = country

    # Ajouter les résultats au DataFrame principal
    results = pd.concat([results, temp_results], ignore_index=True)

# Réorganiser les colonnes pour afficher les résultats par pays en premier
results = results[['Country', 'Culture', 'Proportion']]



'''_____________3. la taille du ménage en Equivalents adultes (EA)_______________________________________'''
# 

#On pondère les enfants par 0,5 en considérant qu'un enfant équivaut 
#à 0,5 adulte 
data_ft['EA'] = (data_ft['HommesadultesHA'] + data_ft['FemmesadultesFA'] +
                 data_ft['VieuxV'] + 0.5 * (data_ft['Garçonsde12ansG12'] + 
                                            data_ft['Fillesde12ansF12']))


'''_____________4. le nombre de mois d’autosuffisance de la production agricole__________________________'''

# 

# Calculer la moyenne du nombre de mois d'autosuffisance par pays
average_autosuffisance_by_country = data_ft.groupby('country')['Nbremoisautosuffis'].mean().reset_index()

# Renommer la colonne pour plus de clarté
average_autosuffisance_by_country.columns = ['Country', 'Average Months Autosuffisance']

print(average_autosuffisance_by_country)


'''_____________5. la taille du cheptel en Unités de bétail tropical (UBT)____________________________'''


# Calculer la taille du cheptel en Unités de Bétail Tropical (UBT)
# Nous utilisons les colonnes `transh_Bovins`, `transh_Ovins` et `transh_Caprins`
# et appliquons les pondérations respectives pour chaque type d'animaux
data_ft['UBT'] = (
    data_ft['transh_Bovins'] * 0.7 +  # Chaque bovin vendu correspond à 0.7 UBT
    data_ft['transh_Ovins'] * 0.15 + # Chaque ovin vendu correspond à 0.15 UBT
    data_ft['transh_Caprins'] * 0.1 + # Chaque caprin vendu correspond à 0.1 UBT
    data_ft['transh_Camelins']  # Chaque camelins vendu correspond à 1 UBT
)


'''_____________6. l’indicateur de viabilité de l’élevage (UBT/EA)________________________________'''

data_ft['viabilite_elevage'] = data_ft['UBT']/data_ft['EA']




viabilite_elevage_pays = data_ft.groupby('country')['UBT'].sum()/data_ft.groupby('country')['EA'].sum()
viabilite_elevage_pays.columns = ['country', 'viabilite_elevage']




'''
===================                                                              ===================

                                2.3 Ventes de bétail durant la transhumance
                             
===================                                                              ===================
'''

'''_____________1. Générer un tableau montrant pour chaque pays le nombre d’observations, la moyenne, la
             médiane, l’écart type, le minimum et le maximum des prix de vente________________________________'''


# Calculer les statistiques descriptives par pays pour la colonne 'Prix'
stats_by_country = data_ventes.groupby('country')['Prix'].agg(
    count='count',     # Nombre d'observations
    mean='mean',       # Moyenne
    median='median',   # Médiane
    std='std',         # Écart type
    min='min',         # Minimum
    max='max'          # Maximum
).reset_index()


'''_____________2. Générer un graphique représentant le prix de vente médian par sexe et par pays_____________'''


# Calculer le prix de vente médian par sexe et par pays
median_price_by_sex_country = data_ventes.groupby(['country', 'Sexe'])['Prix'].median().reset_index()

# Renommer les colonnes pour plus de clarté
median_price_by_sex_country.columns = ['Country', 'Sex', 'Median Price']

# Créer un graphique à barres
plt.figure(figsize=(12, 6))
sns.barplot(x='Country', y='Median Price', hue='Sex', data=median_price_by_sex_country)
plt.title('Median Sales Price by Sex and Country')
plt.xlabel('Country')
plt.ylabel('Median Sales Price')
plt.legend(title='Sex')
plt.xticks(rotation=45)
plt.tight_layout()

# Afficher le graphique
plt.show()

'''_____________3. A travers une régression linéaire, modéliser le prix de vente en fonction du sexe, de l’âge, de
l’origine, du type de client, de la période de vente et du pays. Que peut-on retenir?_____________'''


# Préparer les données
# Convertir les colonnes catégorielles en type 'category'
data_ventes['Sexe'] = data_ventes['Sexe'].astype('category')
data_ventes['Origine'] = data_ventes['Origine'].astype('category')
data_ventes['Aqui'] = data_ventes['Aqui'].astype('category')
data_ventes['Mois'] = data_ventes['Mois'].astype('category')
data_ventes['country'] = data_ventes['country'].astype('category')

# Spécifier la formule de la régression linéaire
formula = 'Prix ~ Sexe + Age + Origine + Aqui + Mois + country'

# Effectuer la régression linéaire
model = smf.ols(formula=formula, data=data_ventes).fit()

# Résumé des résultats de la régression
summary = model.summary()
print(summary)

'''_____________4. Quelles autres variables pourraient être pertinentes à cette régression?_______'''

'''
animal_number : Le numéro de l'animal peut potentiellement capturer des effets de série ou de lot si des lots d'animaux sont vendus ensemble, ce qui pourrait influencer le prix.
Ageapproxans : Une autre mesure de l'âge approximatif de l'animal, qui peut apporter des informations complémentaires à la variable Age.
soudure : Cette variable pourrait indiquer si la vente a eu lieu pendant une période de soudure, où les prix peuvent être affectés par des conditions économiques ou environnementales spécifiques.
'''




'''
===================                                                              ===================

                                    2.4 Elevage et émigration
                             
===================                                                              ===================
'''
'''_____________1. Pour chaque menage, calculer le nombre de personnes qui ont emigre
           durant les 5 annees qui ont precede l’enquete.________________________________________________'''

# Ajouter une colonne pour indiquer si l'émigration est récente (Années < 5)
data_emigration['Recent_Emigration'] = data_emigration['Années'] <= 5

# Calculer le nombre de personnes ayant émigré récemment pour chaque ménage (ID)
nbre_emigres_par_menage = data_emigration.groupby('ID')['Recent_Emigration'].sum().reset_index(name='Nbre_Emigres_5ans')

# Créer un DataFrame contenant tous les ID des ménages
all_menages = pd.DataFrame(data_emigration['ID'].unique(), columns=['ID'])

# Fusionner avec le DataFrame des résultats pour inclure tous les ménages
result = pd.merge(all_menages, nbre_emigres_par_menage, on='ID', how='left')


'''_____________ 2. Calculer l’intensité de l’émigration en rapportant le nombre d’émigrés
 à la taille du ménage.Résumer ce taux par pays.________________________________________________________'''

#

# Calculer le nombre d'émigrés par ménage en comptant le nombre d'apparitions de chaque ID
nbre_emigres_par_menage = data_emigration.groupby('ID').size().reset_index(name='Nbre_Emigres')

total_personnes = data_ft[['HommesadultesHA', 'FemmesadultesFA', 'VieuxV', 'Garçonsde12ansG12', 'Fillesde12ansF12']].sum(axis=1)

# Remplacer les NaN dans la colonne 'Nombretotaldepersonnes' par la somme calculée
data_ft['Nombretotaldepersonnes'] = data_ft['Nombretotaldepersonnes'].fillna(total_personnes)

# Fusionner avec le DataFrame contenant les tailles de ménage
merged_data = pd.merge(data_ft[['ID', 'Nombretotaldepersonnes', 'country']], nbre_emigres_par_menage, on='ID', how='left')

# Calculer l'intensité de l'émigration
merged_data['Intensite_Emigration'] = merged_data['Nbre_Emigres'] / merged_data['Nombretotaldepersonnes']

# Résumer l'intensité de l'émigration par pays

# Calculer l'intensité d'émigration par pays
intensite_emigration_par_pays = merged_data.groupby('country').apply(
    lambda x: x['Nbre_Emigres'].sum() / x['Nombretotaldepersonnes'].sum()
).reset_index(name='Intensite_Emigration')



'''_____________3. Quelles sont les principales destinations des fils d’éleveurs du Sahel?____________'''

# Filtrer les données pour inclure uniquement les fils d'éleveurs du Sahel
fils_sahel = data_emigration[(data_emigration['Liensdeparenté'] == 'fils/fille') & (data_emigration['Région'] == 'Sahel')]

# Compter les occurrences de chaque destination
destinations_counts = fils_sahel['destination'].value_counts().reset_index()
destinations_counts.columns = ['Destination', 'Count']

'''_____________ 4. Quelles sont les destinations principales des émigrés? ____________'''


# Compter les occurrences de chaque destination
destinations_emim_counts = data_emigration['destination'].value_counts().reset_index()
destinations_emim_counts.columns = ['Destination', 'Count']


'''___________ 5. Corréler l’intensité de l’émigration avec l’indicateur de viabilité de l’élevage. Conclure __'''



# Calculer le nombre d'émigrés par ménage en comptant le nombre d'apparitions de chaque ID
nbre_emigres_par_menage = data_emigration.groupby('ID').size().reset_index(name='Nbre_Emigres')

# Fusionner avec le DataFrame contenant les tailles de ménage
merged_data = pd.merge(data_ft[['ID', 'Nombretotaldepersonnes', 'country', 'viabilite_elevage']], nbre_emigres_par_menage, on='ID', how='left')

# Calculer l'intensité de l'émigration
merged_data['Intensite_Emigration'] = merged_data['Nbre_Emigres'] / merged_data['Nombretotaldepersonnes']

# Calculer la corrélation entre l'intensité de l'émigration et l'indicateur de viabilité de l'élevage
correlation = merged_data[['Intensite_Emigration', 'viabilite_elevage']].corr().iloc[0, 1]

# Afficher les résultats
print(f"La corrélation entre l'intensité de l'émigration et l'indicateur de viabilité de l'élevage est de {correlation:.2f}")



'''
===================                                                              ===================
===================                                                              ===================
                                              F I N
===================                                                              ===================                       
===================                                                              ===================
'''