import aiocsv
import aiofiles

class Writer:
    async def create_table(self):
        async with aiofiles.open('data.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = aiocsv.AsyncWriter(f, delimiter=';')
            await writer.writerow(['URL вакансии', 'URL/Название компании-работодателя', 'Присутствующие тэги'])

    async def write_lines(self, lines):
        async with aiofiles.open('data.csv', 'a', encoding='utf-8-sig', newline='') as f:
            writer = aiocsv.AsyncWriter(f, delimiter=';')
            await writer.writerows(lines)