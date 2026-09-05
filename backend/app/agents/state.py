from typing import TypedDict

class ReviewState(TypedDict,total=False):
    paper_id: str 
    methodology_review:dict
    novelty_review:dict
    quality_review:dict
    final_review:dict
