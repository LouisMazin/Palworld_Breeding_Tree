#make a singleton class for the observer manager

class notification_types:
    MAX_TREES = 0
    THEME = 1
    LANGUAGE = 2
    ORDER = 3
    ALL = 4

class ObserverManager:
    _instance = None
    
    def __init__(self):
        self.observers = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, notification_type=notification_types.ALL):
        for observer in self.observers:
            observer.notify(notification_type)