from PageIndex_Logic.query_structure import load_results, answer_question_from_structure
import asyncio

class PageIndex:
    def __init__(self):
        self.results = load_results(r"PageIndex_Logic\results\Brain Tumor MRI.json")

    async def get_answer(self, query):
        return await answer_question_from_structure(
            query=query,
            structure=self.results['structure'],
            model="gpt-oss:120b"
        )

if __name__ == "__main__":
    page_index = PageIndex()
    print(asyncio.run(page_index.get_answer("What is the main topic?")))
