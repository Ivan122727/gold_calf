from storage.parser import parse_users
from gold_calf.settings import BASE_DIRPATH

import asyncio

async def main():
    await parse_users(BASE_DIRPATH + '/storage/salaries.csv')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
