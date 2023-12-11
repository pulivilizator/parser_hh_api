import json
import random
from pprint import pp

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector, ProxyType
import asyncio

from settings import settings, config as settings_config
from . import utils

from configparser import ConfigParser


def get_params(config: ConfigParser) -> list[list[dict]]:
    queryset = config.get('parser', 'tags').split(',')
    return [[{
        'text': query.strip(),
        'page': page,
        'per_page': 100
    } for page in range(20)] for query in queryset]


async def get_present_tags(url: str, tags: str, vacancy_json, session: ClientSession) -> str:
    if url is None:
        return ''
    tags = tags.split()
    await asyncio.sleep(random.randint(1, 20))
    async with session.get(url) as resp:
        resp_text = str(await resp.json()).lower()
        await asyncio.sleep(1)
        present_tags = ', '.join([tag for tag in tags
                                  if tag.strip().lower() in resp_text or tag.strip().lower() in str(vacancy_json).lower()])
        return present_tags


async def get_emp_site(url: str, session: ClientSession) -> str | None:
    if url is None:
        return None
    await asyncio.sleep(random.randint(1, 20))
    async with session.get(url) as resp:
        resp_json = await resp.json()
        if 'site_url' in resp_json:
            return resp_json['site_url']
        return None


async def get_vacancy(params: dict, session: ClientSession) -> dict:
    await asyncio.sleep(params['page'])
    vacancy_urls = []
    async with session.get(url=settings.VACANCIES_API_URL, params=params) as response:
        resp_json = await response.json()
        await asyncio.sleep(15)
    if 'items' in resp_json:
        emp_urls = [i['employer']['url']
                    if 'employer' in i and 'url' in i['employer'] else None
                    for i in resp_json['items']]
        for i in resp_json['items']:
            vacancy_urls.append((i['url'], str(i)))
        vacs_tags = await asyncio.gather(*[asyncio.create_task(get_present_tags(url[0], params['text'], url[1], session)) for url in vacancy_urls])
        await asyncio.sleep(6)
        emp_sites = await asyncio.gather(*[asyncio.create_task(get_emp_site(url, session)) for url in emp_urls])
        for vacancy, site, vac_tags in zip(resp_json['items'], emp_sites, vacs_tags):
            if site:
                vacancy['site_url'] = site
            else:
                vacancy['site_url'] = vacancy['employer']['name']
            vacancy['tags'] = vac_tags
    return resp_json


async def main_vacancies(config: ConfigParser) -> list[tuple]:
    tasks = []
    proxies = settings_config.get_proxies()
    params_lists = utils.split_list(get_params(config), len(proxies))

    for ind, proxy in enumerate(proxies[:len(params_lists)]):
        task = asyncio.create_task(get_vacancies(proxy, params_lists[ind]))
        tasks.append(task)
    vacancies_jsons = await asyncio.gather(*tasks)
    vacancies_gen = (j
                 for i in vacancies_jsons
                 for j in i)
    vacancies = []
    for vac_lst in vacancies_gen:
        if 'items' in vac_lst:
            [vacancies.append((vac['alternate_url'], vac['site_url'], vac['tags'])) for vac in vac_lst['items']]
    return vacancies

async def get_vacancies(proxy: dict, params_lists: list[dict]):
    vacancies_jsons = []
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5,
        host=proxy['server'],
        port=proxy['port'],
        username=proxy['username'],
        password=proxy['password'],
        rdns=True
    )
    async with ClientSession(connector=connector) as session:
        for params_list in params_lists:
            vacs = await asyncio.gather(*[asyncio.create_task(get_vacancy(params, session)) for params in params_list])
            vacancies_jsons.extend(vacs)
            if len(params_lists) > 1:
                await asyncio.sleep(40)

    return vacancies_jsons
