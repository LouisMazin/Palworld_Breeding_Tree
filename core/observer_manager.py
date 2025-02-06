class NotificationTypes:
    MAXTREES = 0
    THEME = 1
    LANGUAGE = 2
    ORDER = 3
    ALL = 4

class ObserverManager:
    _instance = None
    
    def __init__(self):
        self.observers = []

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def addObserver(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)
    
    def removeObserver(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notifyObservers(self, notification_type=NotificationTypes.ALL):
        for observer in self.observers:
            observer.notify(notification_type)