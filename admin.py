from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from functools import wraps

from database import session, get_admins_ids, get_admins_names

def check_admin(func):
    @wraps(func)
    async def wrapper(message: Message, state: FSMContext):
        admins_ids = await get_admins_ids(session)
        admins_usernames = await get_admins_names(session)
        if (message.from_user.username in admins_usernames or
                message.from_user.id in admins_ids):
            return await func(message, state)
        await message.answer('Недостаточно прав!')
        return None
    return wrapper
