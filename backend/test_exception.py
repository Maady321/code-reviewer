import asyncio
import traceback
from app.routes.review_routes import get_review_details
from collections import namedtuple

User = namedtuple('User', ['id'])

async def run():
    try:
        res = await get_review_details('cec7898e-9d7f-45cd-bae0-5461f9bd9836', current_user=User(id='3aac4e9b-8214-4db1-8c96-90feb1251e27'))
        print(res)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
