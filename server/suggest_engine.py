from abc import ABC, abstractmethod
import json


class Suggestion(ABC):
    @abstractmethod
    def __init__(self, params):
        self.params = params
        self.payload = self.params['payload']
        self.config = json.loads(open('./config.json').read())

    @abstractmethod
    def suggest(self):
        """
        This method should retrieve documents for the given query.

        Returns:
        A list of dictionaries, each dictionary contains `Keywords`(List), `type`(String), `MeSH_Terms`(Dictionary)
        where key is index, and value is the MeSH term (String)
        """
        pass
