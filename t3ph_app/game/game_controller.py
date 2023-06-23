
import uuid


from .data import DB
from .entities import Entity
from .events import Encounter


class Game():

    LOAD_ERROR_MSG = 'ERROR! Load game first!'
    INVALID_ENCOUNTER_MSG = 'ERROR! Invalid encounter!'
    LOAD_ENCOUNTER_MSG = 'ERROR! Load encounter first!'

    def __init__(self):
        types = self.get_types()

        self.obj_types = types[0]
        self.data_types = types[1]
        self.commands = self.get_command_list()

        self.loaded_objs = {}

    def get_types(self):
        obj_types = {}
        ent_types = set(Entity.TYPES)

        for ent_type in ent_types:
            obj_types[ent_type] = Entity

        obj_types.update({'encounter' : Encounter})

        data_types = []
        for key in obj_types.keys():
            data_types.append(key)

        return [obj_types, data_types]

    def get_command_list(self):

        commands = {  'load game'    :  self.set_game, 
                      'copy'         :  self.copy_obj,
                      'make'         :  self.make_obj, 
                      'put'          :  self.place_item,
                      'find'         :  self.find,
                      'modify'       :  self.modify_obj,
                      'resolve'      :  self.resolve,
                      'delete'       :  self.delete_obj,
                      'save'         :  self.save_objs,
                      'display'      :  self.display_obj,
                      'remove'       :  self.remove_attribute,
                      'list'         :  self.list_objs,
                      'delete game'  :  Game.remove_game,
                      'list games'   :  Game.list_games}

        return commands

    def set_game(self, system, game):
        self.system = system
        self.game = game

        self.data = DB(self.system, self.game, self.data_types)

    def copy_obj(self, uid):
        obj = self.load_local_obj(uid)
        data_type = obj.data_type

        obj_dict = obj.to_dict()
        obj_dict.pop('data_type')
        obj_dict.pop('uid')

        new_obj = self.make_obj(data_type, **obj_dict)

        return new_obj 

    def make_obj(self, data_type, **kwargs):
        uid = str(uuid.uuid4())
        obj = None
        
        kwargs['data_type'] = data_type

        if data_type in self.obj_types:
            OBJECT = self.obj_types[data_type]
            obj = OBJECT(uid, **kwargs)
            obj_dict = obj.to_dict()
        else:
            return False
        
        try:
            self.data.make(obj_dict, data_type)
        except AttributeError:
            return Game.LOAD_ERROR_MSG

        obj.data_type = data_type
        self.loaded_objs[uid] = obj

        return obj_dict

    def place_item(self, item_uid, container_uid):
        old_container = None

        item = self.load_local_obj(item_uid)
        container = self.load_local_obj(container_uid)
        
        if hasattr(item, 'container'):
            uid = item.container
            old_container = self.load_local_obj(uid)
        
        try:
            status = item.place_item(container, old_container)
        except AttributeError:
            return False

        return status

    def save_obj(self, obj):
        obj_dict = obj.to_dict()
        data_type = obj_dict['data_type']
        
        try:
            self.data.save(obj_dict, data_type)
        except AttributeError:
            return Game.LOAD_ERROR_MSG

    def save_objs(self):
        objs = self.loaded_objs

        for key in objs.keys():
            obj = objs[key]
            self.save_obj(obj)

        self.loaded_objs = {}

        return True

    def display_obj(self, uid):
        obj = self.load_local_obj(uid)
        obj_dict = obj.to_dict()

        return obj_dict

    def load_local_obj(self, uid):
        obj = None
        objs = self.loaded_objs

        for test_uid in objs.keys():
            if test_uid == uid:
                obj = objs[test_uid]
        
        if obj:
            return obj
        else:
            obj_dicts = self.find(None, 'uid', uid)
            return self.load_local_obj(uid)

    def list_objs(self):
        obj_dictionaries = []
        objs = self.loaded_objs

        for uid in objs.keys():
            obj = objs[uid]
            obj_dict = obj.to_dict()

            obj_dictionaries.append(obj_dict)

        return obj_dictionaries

    def dict_to_obj(self, obj_dict):
        data_type = obj_dict['data_type']

        obj_type = self.obj_types[data_type]
        obj = obj_type.from_dict(obj_dict)

        return obj

    def find(self, data_type, search_key, search_value):
        obj_dicts = [] 
        
        if not data_type:
            for data_type in self.data_types:
                obj_dicts += self.find(data_type, search_key, search_value)
            return obj_dicts
        
        try:
            if search_key and search_value:
                results = self.data.find(data_type, {search_key : search_value})
            else:
                results = self.data.find(data_type)
        except AttributeError:
            return Game.LOAD_ERROR_MSG

        results = list(results)

        if results:
            for result in results:
                del result['_id']
                obj = self.dict_to_obj(result)
                obj_dict = obj.to_dict()

                self.loaded_objs[obj.uid] = obj
                obj_dicts.append(obj_dict)
        
        return obj_dicts

    def delete_obj(self, uid):
        objs = self.loaded_objs
        objs_copy = objs.copy()

        for test_uid in objs_copy.keys():
            if test_uid == uid:
                obj = objs_copy[uid]
                data_type = obj.data_type

                del objs[test_uid]

                try:
                    self.data.remove(uid, data_type)
                except AttributeError:
                    return Game.LOAD_ERROR_MSG
                
                return True

        return False
        
    def remove_attribute(self, uid, attribute):
        obj = self.load_local_obj(uid)
        attribute = attribute.lower()

        illegal = ['name', 'uid', 'data_type']

        if obj and attribute not in illegal and hasattr(obj, attribute):
            del obj.__dict__[attribute]
            return True
        else:
            return False

    def modify_obj(self, uid, **kwargs):
        obj = self.load_local_obj(uid)
        
        if obj:
            obj_dict = obj.to_dict()

            for key, value in kwargs.items():
                if type(value) is dict and key in obj_dict.keys():
                    dictionary = obj_dict[key]
                    new_dict = {**dictionary, **value}

                    obj_dict[key] =  new_dict

                elif type(value) is list and key in obj_dict.keys():
                    obj_list = obj_dict[key]
                    new_list = obj_list + value

                    obj_dict[key] = new_list

                else:
                    obj_dict[key] = value

            obj = self.dict_to_obj(obj_dict)
            
            del self.loaded_objs[uid]
            self.loaded_objs[uid] = obj
        else:
            return False

    def list_games():
        games = DB.list_databases()
        return games

    def remove_game(system, game):
        status = DB.delete_game(system, game)
        return status

#   def resolve(self, encounter_uid, **kwargs):
    def resolve(self, encounter_uid):
        encounter_obj = self.load_local_obj(encounter_uid)

        try:
            entity_uids = encounter_obj.get_entities()
        except AttributeError:
            return Game.LOAD_ENCOUNTER_MSG
        
        entities = []
        if entity_uids:
            for uid in entity_uids:
                entity = self.load_local_obj(uid)
                entities.append(entity)
#
#        if kwargs:
#            for key, value in kwargs.items():
#                try:
#                    uuid.UUID(value)
#                    entity= self.load_local_obj(uid)
#                    entities.append(entity)
#
#                except:
#                    pass
#
#        outcome = encounter_obj.resolve(entities, **kwargs)
        
        try:
            outcome = encounter_obj.resolve(entities)
        except AttributeError:
            return Game.INVALID_ENCOUNTER_MSG
        
        entities_dicts = []
        for entity in entities:
            entities_dicts.append(entity.to_dict())
        
        return outcome, entities_dicts

    def get_inputs(self, encounter):
        inputs = encounter.get_inputs()
        return inputs

    def get_entities(self, encounter):
        entities = encounter.get_entitites()
        return entities
