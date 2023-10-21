import json
import logging
import platform
import asyncio
import sys
from datetime import date, timedelta
import aiohttp


# перевіряє чи кількість днів не більша 10
async def check_days(days: int):
    if days > 10:
        logging.info('Can not check data before more than 10 days')
        quit()


#повертає дату враховуючи зміщення
async def get_date_with_delta(days: int) -> str:
    return (date.today() - timedelta(days=days)).strftime('%d.%m.%Y')


#створює фінальний словник для заданої дати
async def create_result_dict(json_data: dict, date: str) -> dict:
    eur_usd_list = list(filter(lambda d: d['currency'] in ['EUR', 'USD'], json_data['exchangeRate']))
    eur_usd_list = [{'EUR': {'sale': eur_usd_list[0]['saleRateNB'], 'purchase': eur_usd_list[0]['purchaseRateNB']}},
                    {'USD': {'sale': eur_usd_list[1]['saleRateNB'], 'purchase': eur_usd_list[1]['purchaseRateNB']}}]
    res = {date: {}}
    for dictionary in eur_usd_list:
        res[date].update(dictionary)
    return res


async def main(days: int):
    await check_days(days)
    async with aiohttp.ClientSession() as session:
        res = []
        for i in range(days):
            date = await get_date_with_delta(i)
            url = f'https://api.privatbank.ua/p24api/exchange_rates?date={date}'
            try:
                async with session.get(url) as exchange:
                    if exchange.status == 200:
                        json_data = await create_result_dict(await exchange.json(), date)
                        res.append(json_data)
                    else:
                        logging.info(f'Error status: {exchange.status}')
            except aiohttp.ClientConnectorError as err:
                logging.info(f'Connection error: {url}', str(err))
        return res


if __name__ == '__main__':
    logging.basicConfig(level='INFO', format='%(message)s')
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(json.dumps(asyncio.run(main(int(sys.argv[1]))), indent=4))
