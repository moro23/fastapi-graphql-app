import strawberry
import asyncio 
from typing import AsyncGenerator, Optional
from strawberry.types import Info
from .types import FAQItemType, FeedbackType 


@strawberry.type 
class Subscription:
    @strawberry.subscription 
    async def count(self, target: int = 10) -> AsyncGenerator[int, None]:
        """A simple subscription that counts up to a target number."""
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)