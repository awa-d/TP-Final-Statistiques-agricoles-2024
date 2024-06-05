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
data_ft['EA'] = (data_ft['HommesadultesHA'] + data_ft['FemmesadultesFA'] +
                 data_ft['VieuxV'] + 0.5 * (data_ft['Garçonsde12ansG12'] + 
                                            data_ft['Fillesde12ansF12']))
data_ft['UBT'] = (
    data_ft['transh_Bovins'] * 0.7 +  # Chaque bovin vendu correspond à 0.7 UBT
    data_ft['transh_Ovins'] * 0.15 + # Chaque ovin vendu correspond à 0.15 UBT
    data_ft['transh_Caprins'] * 0.1 + # Chaque caprin vendu correspond à 0.1 UBT
    data_ft['transh_Camelins']  # Chaque camelins vendu correspond à 1 UBT
)
data_ft['viabilite_elevage'] = data_ft['UBT']/data_ft['EA']


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