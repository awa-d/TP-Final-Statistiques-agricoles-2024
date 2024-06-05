'''______________________________________________________________________________________________

   T R A V A U X   P R A T I Q U E S   F I N A U X   D E   S T A T I S T I Q U E S   A G R I C O L E S 
   
                              E L E V A G E     P A S T O R A L E 
             __________________________________________________________________________
              
                  Rédigé par Awa DIAW et Malick SENE  élèves en ISEP 2 à l'ENSAE
               
'''

                                     ##Import libraries##
import pandas as pd
                                     ##Import dataset##
data_emigration = pd.read_stata("emigration_cleaned.dta")
data_ft = pd.read_stata("data_FT.dta")

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

print(results)


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

viabilite_elevage = data_ft.groupby('country')['UBT'].sum()/data_ft.groupby('country')['EA'].sum()
viabilite_elevage.columns = ['country', 'viabilite_elevage']

