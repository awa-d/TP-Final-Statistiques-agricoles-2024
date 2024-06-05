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
data_ventes = pd.read_stata("vente_betail_cleaned.dta")
data_ft = pd.read_stata("data_FT.dta")


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

print(stats_by_country)

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
Animal_number : Le numéro de l'animal peut potentiellement capturer des effets de série ou de lot si des lots d'animaux sont vendus ensemble, ce qui pourrait influencer le prix.
Ageapproxans : Une autre mesure de l'âge approximatif de l'animal, qui peut apporter des informations complémentaires à la variable Age.
soudure : Cette variable pourrait indiquer si la vente a eu lieu pendant une période de soudure, où les prix peuvent être affectés par des conditions économiques ou environnementales spécifiques.
'''



