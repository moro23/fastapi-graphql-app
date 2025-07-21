import strawberry 
from typing import List, Optional 
from pydantic import UUID4 


@strawberry.input 
class FAQCategoryInput: 
    name: str 
    description: Optional[str] = None


@strawberry.input 
class FAQItemInput:
    question: str
    answer: str
    category_id: strawberry.ID 
    tags: Optional[str] = None 
    is_published: Optional[bool] = True

@strawberry.input 
class FAQItemUpdateInput:
    question: Optional[str] = None
    answer: Optional[str] = None
    category_id: Optional[strawberry.ID] = None
    tags: Optional[str] = None
    is_published: Optional[bool] = None

@strawberry.input 
class FeedbackInput:
    comment: str 
    faq_item_id: Optional[strawberry.ID] = None
    rating: Optional[int] = None 
    contact_email: Optional[str] = None  