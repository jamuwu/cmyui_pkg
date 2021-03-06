# -*- coding: utf-8 -*-

import asyncpg
from typing import Dict, List, Tuple, Optional, Union, AsyncGenerator

__all__ = (
    'SQLParams',
    'SQLResult',
    'AsyncPGPool'
)

SQLParams = Tuple[Union[int, float, str]]
SQLResult = asyncpg.Record


class AsyncPGPool:
    __slots__ = ('pool',)

    def __init__(self):
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def connect(self, loop, **kwargs):
        self.pool = await asyncpg.create_pool(loop=loop, **kwargs)

    async def execute(self, query: str, *params: Tuple[SQLParams]) -> int:
        async with self.pool.acquire() as con:
            async with con.transaction():
                res = await con.cursor(query, *params)
        
        return res

    async def fetch(self, query: str, *params: Tuple[SQLParams], _all: bool = False
                   ) -> Optional[Union[List[SQLResult], SQLResult]]:
        async with self.pool.acquire() as con:
            async with con.transaction():
                cur = await con.cursor(query, *params)
                res = await (cur.fetch if _all else cur.fetchrow)()

        return res

    async def fetchall(self, query: str, *params: Tuple[SQLParams]
                      ) -> Optional[Union[Tuple[SQLResult], SQLResult]]:
        return await self.fetch(query, *params, _all = True)

    async def iterall(self, query: str, *params: Tuple[SQLParams]
                     ) -> AsyncGenerator[SQLResult, None]:
        async with self.pool.acquire() as con:
            async with con.transaction():
                async for record in con.cursor(query, *params):
                    yield record