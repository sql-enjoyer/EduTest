
class Task:
    def __init__(self, task_id, text, answer):
        self.id = task_id
        self.text = text
        self.answer = answer
    
    def get_id(self):
        return self.id
    
    def get_text(self):
        return self.text
    
    def get_answer(self):
        return self.answer
