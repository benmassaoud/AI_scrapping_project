import asyncio
from Projects.Duproprio.Project_Duproprio import Duproprio


async def main():
    dup = Duproprio(
        "https://duproprio.com/fr/rechercher/liste?search=true&type[0]=house&subtype[0]=1&subtype[1]=2&subtype[2]=4&subtype[3]=5&subtype[4]=6&subtype["
        "5]=7&subtype[6]=9&subtype[7]=10&subtype[8]=11&subtype[9]=13&subtype[10]=15&subtype[11]=17&subtype[12]=19&subtype[13]=21&subtype[14]=97&subtype["
        "15]=99&subtype[16]=100&is_for_sale=1&with_builders=1&parent=1&pageNumber={}&sort=-published_at")
    await dup.start_scrapping(1, 20) # de quelle page de recherche à quelle page, chaque page de recherche contient 11 urls
    # to Dataframe
    df = dup.scrapped_data_to_dataframe()
    print(df.info())

    # to excel
    dup.scrapped_data_to_excel('duproprio_extract')

asyncio.run(main())

