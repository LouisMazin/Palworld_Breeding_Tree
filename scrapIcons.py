import requests

# URL of the page
pageUrl = 'https://palworld.wiki.gg/wiki/'

palList = ['Lamball', 'Cattiva', 'Chikipi', 'Lifmunk', 'Foxparks', 'Fuack', 'Sparkit', 'Tanzee', 'Rooby', 'Pengullet', 'Penking', 'Jolthog', 'Jolthog Cryst', 'Gumoss', 'Vixy', 'Hoocrates', 'Teafant', 'Depresso', 'Cremis', 'Daedream', 'Rushoar', 'Nox', 'Fuddler', 'Killamari', 'Mau', 'Mau Cryst', 'Celaray', 'Direhowl', 'Tocotoco', 'Flopie', 'Mozzarina', 'Bristla', 'Gobfin', 'Gobfin Ignis', 'Hangyu', 'Hangyu Cryst', 'Mossanda', 'Mossanda Lux', 'Woolipop', 'Caprity', 'Melpaca', 'Eikthyrdeer', 'Eikthyrdeer Terra', 'Nitewing', 'Ribbuny', 'Incineram', 'Incineram Noct', 'Cinnamoth', 'Arsox', 'Dumud', 'Cawgnito', 'Leezpunk', 'Leezpunk Ignis', 'Loupmoon', 'Galeclaw', 'Robinquill', 'Robinquill Terra', 'Gorirat', 'Beegarde', 'Elizabee', 'Grintale', 'Swee', 'Sweepa', 'Chillet', 'Univolt', 'Foxcicle', 'Pyrin', 'Pyrin Noct', 'Reindrix', 'Rayhound', 'Kitsun', 'Dazzi', 'Lunaris', 'Dinossom', 'Dinossom Lux', 'Surfent', 'Surfent Terra', 'Maraith', 'Digtoise', 'Tombat', 'Lovander', 'Flambelle', 'Vanwyrm', 'Vanwyrm Cryst', 'Bushi', 'Beakon', 'Ragnahawk', 'Katress', 'Wixen', 'Verdash', 'Vaelet', 'Sibelyx', 'Elphidran', 'Elphidran Aqua', 'Kelpsea', 'Kelpsea Ignis', 'Azurobe', 'Cryolinx', 'Blazehowl', 'Blazehowl Noct', 'Relaxaurus', 'Relaxaurus Lux', 'Broncherry', 'Broncherry Aqua', 'Petallia', 'Reptyro', 'Reptyro Cryst', 'Kingpaca', 'Kingpaca Cryst', 'Mammorest', 'Mammorest Cryst', 'Wumpo', 'Wumpo Botan', 'Warsect', 'Fenglope', 'Felbat', 'Quivern', 'Blazamut', 'Helzephyr', 'Astegon', 'Menasting', 'Anubis', 'Jormuntide', 'Jormuntide Ignis', 'Suzaku', 'Suzaku Aqua', 'Grizzbolt', 'Lyleen', 'Lyleen Noct', 'Faleris', 'Orserk', 'Shadowbeak', 'Paladius', 'Necromus', 'Frostallion', 'Frostallion Noct', 'Jetragon', 'Bellanoir', 'Bellanoir Libero']

for pal in palList:
    tempUrl = pageUrl + pal.replace(' ', '_')
    response = requests.get(tempUrl)
    imageUrl = pageUrl[0:-6] + str(response.text.split('title="Icon"')[1].split('src="')[1].split('"')[0])
    #download the image
    with open('Temp/' + pal + '.png', 'wb') as f:
        f.write(requests.get(imageUrl).content)