import pandas as pd

df = pd.read_excel('cards_info.xlsx', usecols=['Set #', 'Name'])
print('Total cartes:', len(df))
print('\nPremières 10 cartes:')
for i in range(10):
    print(f'{i}: {df.iloc[i]["Set #"]} - {df.iloc[i]["Name"]}')

print('\nCartes uniques par Set#:', df['Set #'].nunique())
print('Cartes uniques par Name:', df['Name'].nunique())

# Vérifier s'il y a des doublons
print('\n=== Vérification des doublons de Set# ===')
duplicates = df[df.duplicated(subset=['Set #'], keep=False)]
if len(duplicates) > 0:
    print(f'ATTENTION: {len(duplicates)} doublons trouvés!')
    print(duplicates[['Set #', 'Name']].head(20))
else:
    print('Aucun doublon de Set#')
