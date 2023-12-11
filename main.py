import asyncio

from settings.config import get_config

from parser.app import app
from parser.sheets_writer.writer import Writer

async def main():
    config = get_config()
    vacs = await app(config)


if __name__ == '__main__':
    asyncio.run(main())
