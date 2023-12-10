from .vacancies import main_vacancies
from .sheets_writer.writer import Writer

from pprint import pp
from configparser import ConfigParser

async def app(config: ConfigParser):
    writer = Writer()
    await writer.create_table()
    vacs = await main_vacancies(config)
    await writer.write_lines(vacs)
    return vacs