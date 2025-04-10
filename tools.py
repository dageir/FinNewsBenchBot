import uuid
from datetime import datetime

async def generate_filename(id: str, username: str) -> str:
    return f'{id}_{username}_{uuid.uuid4()}.xlsx'

async def generate_short_filename(username: str) -> str:
    now_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f'{username}_{now_date}.xlsx'
