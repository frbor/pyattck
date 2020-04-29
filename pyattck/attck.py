import warnings

from .configuration import Configuration
from .datasets import AttckDatasets


class Attck(object):

    '''
        This class creates an interface to all Mitre ATT&CK frameworks.

        Currently, this class only enables access to the Enterprise framework with others coming soon.

        This interface enables you to retrieve all properties within each item in the Mitre ATT&CK Enterprise Framework.

        The following categorical items can be accessed using this class:

            1. Tactics (Tactics are the phases defined by Mitre ATT&CK)
            2. Techniques (Techniques are the individual actions which can accomplish a tactic)
            3. Mitigations (Mitigations are recommendations to prevent or protect against a technique)
            4. Actors (Actors or Groups are identified malicious actors/groups which have been identified and documented by Mitre & third-parties)
            5. Tools (Tools are software used to perform techniques)
            6. Malwares (Malwares are specific pieces of malware used by actors (or in general) to accomplish a technique)

        You can also search the external dataset for external commands that are similar using the `search_commands` method.

           .. code-block:: python
               
               from pyattck import Attck

               attck = Attck()
               
               for search in attck.enterprise.search_commands('powershell'):
                   print(search['technique'])
                   print(search['reason_for_match'])

        Additionally, as of pyattck 2.0.0 you can now access additional datasets related to a technique.
        These datasets are [documented here](https://github.com/swimlane/pyattck/blob/master/generateattcks/README.md).
    
    Example:
        Once an Attck object is instantiated, you can access each object type as a list of objects (e.g. techniques, tactics, actors, etc.)

        You can iterate over each object list and access specific properties and relationship properties of each.
        
        The following relationship properties are accessible:
            1. Actors
                1. Tools used by the Actor or Group
                2. Malware used by the Actor or Group
                3. Techniques this Actor or Group uses
            2. Malwares
                1. Actor or Group(s) using this malware
                2. Techniques this malware is used with
            3. Mitigations
                1. Techniques related to a specific set of mitigation suggestions
            4. Tactics
                1. Techniques found in a specific Tactic (phase)
            5. Techniques
                1. Tactics a technique is found in
                2. Mitigation suggestions for a given technique
                3. Actor or Group(s) identified as using this technique
            6. Tools
                1. Techniques that the specified tool is used within
                2. Actor or Group(s) using a specified tool
        
            1. To iterate over a list, do the following:

            .. code-block:: python
               
               from pyattck import Attck

               attck = Attck()
               
               for technique in attck.enterprise.techniques:
                   print(technique.id)
                   print(technique.name)
                   print(technique.description)
                   # etc.
               for mitigation in attck.enterprise.mitigations:
                   print(mitigation.id)
                   print(mitigation.name)
                   print(mitigation.description)
                   # etc.

            2. To access relationship properties, do the following:

            .. code-block:: python

               from pyattck import Attck

               attck = Attck()
               
               for technique in attck.enterprise.techniques:
                   print(technique.id)
                   print(technique.name)
                   print(technique.description)
                   # etc.

                   for actor in technique.enterprise.actors:
                       print(actor.id)
                       print(actor.name)
                       print(actor.description)
                       # etc.

               for mitigation in attck.enterprise.mitigations:
                   print(mitigation.id)
                   print(mitigation.name)
                   print(mitigation.description)
                   # etc.

                   for technique in mitigation.enterprise.techniques:
                       print(technique.name)
                       print(technique.description)
                       # etc.

    Arguments:
        attck_json (json) - The attck_json is supplied by the attck.py module when instantiated.

    Returns:
        [Attck]: Returns a Attck object that contains all data from the Mitre ATT&CK Framework
    '''

    __ENTERPRISE_ATTCK_JSON = None
    __MOBILE_ATTCK_JSON = None
    __PRE_ATTCK_JSON = None
    __ENTERPRISE_GENERATED_DATA_JSON = None

    __tactics = None
    __techniques = None
    __mitigations = None
    __actors = None
    __tools = None
    __malwares = None

    def __init__(self, subtechniques=False, attck_json=None, dataset_json=None, config_path=None, force=False):
        """The main entry point for pyattck.

        When instantiating an Attck object you can currently access the Enterprise Mitre ATT&CK Framework.

        You can specify an alternate location of a local copy of the following objects:

            1. attck_json = Path to the Mitre ATT&CK Enterprise Framework json
            2. dataset_json = Path to a local dataset json file which is generated in the pyattck repo
            3. config_path = Path to a yaml configuration file which contains two key value pairs
                Example content:

                    enterprise_attck_dataset: /Users/first.last/pyattck/enterprise_attck_dataset.json
                    enterprise_attck_json: /Users/first.last/pyattck/enterprise_attck.json
        
        Args:
            attck_json (str, optional): Path to the Mitre ATT&CK Enterprise Framework json. Defaults to None.
            dataset_json (str, optional): Path to a local dataset json file which is generated in the pyattck repo. Defaults to None.
            config_path (str, optional): Path to a yaml configuration file which contains two key value pairs. Defaults to None.
            force (bool, optional): Force reset configuration file and paths.  Defaults to False.
        """
        self.subtechniques = subtechniques
        if config_path:
            Configuration.__CONFIG_FILE = config_path
        if attck_json or dataset_json:
            Configuration().set(enterprise_attck_json_path=attck_json, enterprise_attck_dataset_path=dataset_json)
        if force:
            Configuration().set()
        self.__datasets = AttckDatasets()
        self.__load_data()

    @property
    def enterprise(self):
        """Retrieve objects from the Enterprise MITRE ATT&CK Framework and additional generated data which provides additional context
        
        Returns:
            Enterprise: Returns an Enterprise object
        """        
        from .enterprise.enterprise import Enterprise
        return Enterprise(self.__ENTERPRISE_ATTCK_JSON)

    @property
    def actors(self):
        """Creates AttckActor objects

        This property will be deprecated in a future release.  Please use the Enterprise property to access these objects.
        
        Returns:
            (AttckActor) -- (Returns a list of AttckActor objects)
        """
        warnings.warn(
            '''Accessing actors property from an Attck object will be depreciated in version 3.
            
            Please begin migrating to accessing the Enterprise Mitre ATT&CK objects using the enterprise property''',
            DeprecationWarning)
        from .enterprise.actor import AttckActor
        if self.__actors is None:
            self.__actors = []
            for group in self.__ENTERPRISE_ATTCK_JSON['objects']:
                if group['type'] == 'intrusion-set':
                    self.__actors.append(AttckActor(attck_obj=self.__ENTERPRISE_ATTCK_JSON, **group))
        return self.__actors

    @property
    def tactics(self):
        """Creates AttckTactic objects

        This property will be deprecated in a future release.  Please use the Enterprise property to access these objects.
        
        Returns:
            (AttckTactic) -- (Returns a list of AttckTactic objects)
        """
        warnings.warn(
            '''Accessing tactics property from an Attck object will be depreciated in version 3.
            
            Please begin migrating to accessing the Enterprise Mitre ATT&CK objects using the enterprise property''',
            DeprecationWarning)
        from .enterprise.tactic import AttckTactic
        if self.__tactics is None:
            self.__tactics = []
            for tactic in self.__ENTERPRISE_ATTCK_JSON['objects']:
                if tactic['type'] == 'x-mitre-tactic':
                    self.__tactics.append(AttckTactic(attck_obj=self.__ENTERPRISE_ATTCK_JSON, **tactic))
        return self.__tactics

    @property
    def mitigations(self):
        """Creates AttckMitigation objects

        This property will be deprecated in a future release.  Please use the Enterprise property to access these objects.
        
        Returns:
            (AttckMitigation) -- (Returns a list of AttckMitigation objects)
        """
        warnings.warn(
            '''Accessing mitigations property from an Attck object will be depreciated in version 3.
            
            Please begin migrating to accessing the Enterprise Mitre ATT&CK objects using the enterprise property''',
            DeprecationWarning)
        from .enterprise.mitigation import AttckMitigation
        if self.__mitigations is None:
            self.__mitigations = []
            for mitigation in self.__ENTERPRISE_ATTCK_JSON['objects']:
                if mitigation['type'] == 'course-of-action':
                    self.__mitigations.append(AttckMitigation(attck_obj=self.__ENTERPRISE_ATTCK_JSON, **mitigation))
        return self.__mitigations

    @property
    def tools(self):
        """Creates AttckTools objects

        This property will be deprecated in a future release.  Please use the Enterprise property to access these objects.
        
        Returns:
            (AttckTools) -- Returns a list of AttckTools objects
        """
        warnings.warn(
            '''Accessing tools property from an Attck object will be depreciated in version 3.
            
            Please begin migrating to accessing the Enterprise Mitre ATT&CK objects using the enterprise property''',
            DeprecationWarning)
        from .enterprise.tools import AttckTools
        if self.__tools is None:
            self.__tools = []
            for tools in self.__ENTERPRISE_ATTCK_JSON['objects']:
                if (tools['type'] == 'tool'):
                    self.__tools.append(AttckTools(attck_obj=self.__ENTERPRISE_ATTCK_JSON, **tools))
        return self.__tools

    @property
    def malwares(self):
        """Creates AttckMalware objects

        This property will be deprecated in a future release.  Please use the Enterprise property to access these objects.
        
        Returns:
            (AttckMalware) -- Returns a list of AttckMalware objects
        """
        warnings.warn(
            '''Accessing malwares property from an Attck object will be depreciated in version 3.
            
            Please begin migrating to accessing the Enterprise Mitre ATT&CK objects using the enterprise property''',
            DeprecationWarning)
        from .enterprise.malware import AttckMalware
        if self.__malwares is None:
            self.__malwares = []
            for malware in self.__ENTERPRISE_ATTCK_JSON['objects']:
                if (malware['type'] == 'malware'):
                    self.__malwares.append(AttckMalware(attck_obj=self.__ENTERPRISE_ATTCK_JSON, **malware))
        return self.__malwares

    @property
    def techniques(self):
        """Creates AttckTechnique objects

        This property will be deprecated in a future release.  Please use the Enterprise property to access these objects.
        
        Returns:
            (AttckTechnique) -- Returns a list of AttckTechnique objects
        """
        warnings.warn(
            '''Accessing techniques property from an Attck object will be depreciated in version 3.
            
            Please begin migrating to accessing the Enterprise Mitre ATT&CK objects using the enterprise property''',
            DeprecationWarning)
        from .enterprise.technique import AttckTechnique
        if self.__techniques is None:
            self.__techniques = []
            for technique in self.__ENTERPRISE_ATTCK_JSON["objects"]:
                if (technique['type'] == 'attack-pattern'):
                    self.__techniques.append(AttckTechnique(attck_obj=self.__ENTERPRISE_ATTCK_JSON, **technique))
        return self.__techniques

    def update(self):
        """
        Calling this method will force update / sync all datasets from external sources
        """
        self.__load_data(force=True)

    def __load_data(self, force=False):
        if not Attck.__ENTERPRISE_ATTCK_JSON:
            if self.subtechniques:
                Attck.__ENTERPRISE_ATTCK_JSON = self.__datasets.mitre(force=force, subtechniques=True)
            else:
                Attck.__ENTERPRISE_ATTCK_JSON = self.__datasets.mitre(force=force)
        if not Attck.__ENTERPRISE_GENERATED_DATA_JSON:
            Attck.__ENTERPRISE_GENERATED_DATA_JSON = self.__datasets.generated_attck_data(force=force)