import datetime
import logging
import platform
import asyncio
from datetime import datetime, timedelta

import aiohttp


async def check_days(days: int):
    if days > 10:
        logging.info('Can not check data before more than 10 days')
        quit()


async def get_date_with_delta(days: int) -> str:
    date = datetime.now().date() - timedelta(days=days)
    date = date.strftime('%d.%m.%Y')
    return date

async def parse_json(json: dict):
    eur_usd_list = list(filter(lambda d: d['currency'] in ['EUR', 'USD'], json['exchangeRate']))
    eur_usd_list = [{'EUR': {'sale': eur_usd_list[0]['saleRateNB'], 'purchase': eur_usd_list[0]['purchaseRateNB']}},
                    {'USD': {'sale': eur_usd_list[1]['saleRateNB'], 'purchase': eur_usd_list[1]['purchaseRateNB']}}]
    return eur_usd_list

async def main(days: int):
    await check_days(days)
    async with aiohttp.ClientSession() as session:
        date = await get_date_with_delta(days)
        url = f'https://api.privatbank.ua/p24api/exchange_rates?date={date}'
        try:
            async with session.get(url) as exchange:
                if exchange.status == 200:
                    json = await exchange.json()
                    parsed_json = await parse_json(json)
                    print(parsed_json)

                else:
                    logging.info(f'Error status: {exchange.status}')
        except aiohttp.ClientConnectorError as err:
            logging.info(f'Connection error: {url}', str(err))


if __name__ == '__main__':
    logging.basicConfig(level='INFO', format='%(message)s')
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(10))
