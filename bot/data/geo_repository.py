import aiosqlite
from bot.data.base_repository import BaseRepository
from bot.models.class_models import leaderboard as leaderboardDC


class geo_repository(BaseRepository):

    async def get_rank(self) -> list[leaderboardDC]:
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT *, ROW_NUMBER() OVER(ORDER BY score DESC) AS RANK from leaderboard')
            return await self.fetch_all_as_dict(cursor)

    async def return_size(self) -> list[leaderboardDC]:
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT COUNT(*) FROM leaderboard;')
            return await self.fetch_all_as_dict(cursor)

    async def update_score(self, score, user_id):
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            await connection.execute('UPDATE leaderboard SET score = ? WHERE user_id = ?;', (score, user_id,))
            await connection.commit()

    async def sort_and_return(self) -> list[leaderboardDC]:
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10;')
            return await self.fetch_all_as_dict(cursor)

    async def get_existing_score(self, user_id):
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT score FROM leaderboard WHERE user_id = ? LIMIT 1;', (user_id,) )
            dictionary = await self.fetch_first_as_dict(cursor)
            if not dictionary:
                return None
            return dictionary

    async def check_if_user_exists(self, user_id) -> list[leaderboardDC]:
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT COUNT(*) FROM leaderboard WHERE user_id = :userid', {"userid": user_id})
            return await self.fetch_all_as_dict(cursor)

    async def add_into(self, name, user_id, rank, score):
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            await connection.execute('INSERT INTO leaderboard (name, user_id, rank, score, RANK) values (?, ?, ?, ?, 0);', (name, user_id, rank, score))
            await connection.commit()

    #delete a user
    async def reset(self, user_id):
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            await connection.execute('DELETE FROM leaderboard WHERE user_id = ?', (user_id,) )
            await connection.commit()

    async def get_all_members(self) -> list[leaderboardDC]:
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT * FROM leaderboard;')
            return [leaderboardDC(**d) for d in await self.fetch_all_as_dict(cursor)]

    async def get_members_by_name(self, name) -> list[leaderboardDC]:
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT * FROM leaderboard WHERE name = ?;', (name,))
            return [leaderboardDC(**d) for d in await self.fetch_all_as_dict(cursor)]

    async def get_best_preparation_for_member(self, user_id):
        async with aiosqlite.connect(self.resolved_db_path) as connection:
            cursor = await connection.execute('SELECT * FROM leaderboard WHERE user_id = ? ORDER BY score DESC LIMIT 1;', (user_id,))
            dictionary = await self.fetch_first_as_dict(cursor)
            if not dictionary:
                return None
            return leaderboardDC(**dictionary)