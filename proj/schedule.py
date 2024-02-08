from datetime import datetime


class Job:
    __identifier = 0
    
    def __init__(self, name, duration, deadline, importance):
        Job.__identifier += 1
        self._id = self.__identifier
        self.name = name
        self.duration = duration
        self.deadline = deadline
        self.importance = importance

    @property
    def description(self):
        dt = datetime.fromtimestamp(self.deadline)
        return dt.strftime("%d-%m-%Y %I:%M %p")
    
    @property
    def getduration(self):
        return f"{self.duration//3600:02d}:{(self.duration%3600)//60:02d}"

    def __repr__(self):
        return f"Job({self._id}, {self.duration}, {self.deadline}, {self.importance})"
    
    def __lt__(self, o):
        return self.deadline < o.deadline
    
    
class Task:
    def __init__(self, _id, dur, imp):
        self._id = _id
        self.dur = dur
        self.imp = imp
        
    def __repr__(self):
        return f"Task({self._id}, {self.dur}, {self.imp})"
    
    def __lt__(self, o):
        if(self.imp == o.imp):
            return self.dur < o.dur
        else:
            return self.imp