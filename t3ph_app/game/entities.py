
class Entity():
    #potential kwargs: info, resources, encounters, items, locations, characters

    #resources = dictionary with resource name as key and int as value

    #encounters = list of encounter objects

    #items = list of entity objects with item entity type

    #places = list of entity objects with place entity type

    #characters = list of entity objects with character entity type
    
    TYPES = ('item', 'place', 'character')

    def __init__(self, uid, name='unnamed_entity', **kwargs):
        self.uid = uid
        self.name = name
        self.data_type = kwargs.pop('data_type')
        
        if self.data_type not in Entity.TYPES:
            raise InvalidEntityTypeException(self.data_type)

        self.__dict__.update(kwargs)

    def __get_space(self):
        itm_size = 0
        itm_inv = 0

        if hasattr(self, 'resources'):
            if 'size' in self.resources:
                itm_size = self.resources['size']
            if 'inventory' in self.resources:
                itm_inv = self.resources['inventory']

        itm_space = itm_size + itm_inv
        return itm_space

    def __check_container(self, container):
        cntnr_size = 0
        cntnr_inv = 0

        itm_space = self.__get_space()

        new_inv = 0

        if hasattr(container, 'resources') and 'inventory' in container.resources:
            cntnr_inv = container.resources['inventory']
            cntnr_size = container.resources['size']
        
        new_inv = cntnr_inv + itm_space

        if cntnr_size >= itm_space and new_inv <= cntnr_size:
            return True
        else:
            return False 
                
    def __add_item(self, container, data_type_list):
        itm_space = self.__get_space()

        if itm_space != 0:
            container.resources['inventory'] += itm_space

        if hasattr(container, data_type_list):
            container.__dict__[data_type_list].append(self.uid)
        else:
            container.__dict__[data_type_list] = [self.uid]
                
        self.container = container.uid

    def __remove_item(self, container, data_type_list):
        itm_space = self.__get_space()

        if hasattr(container, 'resources'):
            if 'inventory' in container.resources:
                container.resources['inventory'] -= itm_space
            
        container.__dict__[data_type_list].remove(self.uid)

        if not container.__dict__[data_type_list]:
            del container.__dict__[data_type_list]

    def place_item(self, container, old_container = None):
        data_type_list = self.data_type + 's'
        itm_space = self.__get_space()
            
        if self.__check_container(container):
            self.__add_item(container, data_type_list) 
        elif itm_space == 0:
            self.__add_item(container, data_type_list)
        else:
            return False
        
        if old_container:
            self.__remove_item(old_container, data_type_list)

        return True

    def __str__(self):
        return str(self.name)

    def to_dict(self):
        return self.__dict__.copy()

    def from_dict(entity_dict):
        entity_dict = entity_dict.copy()
        uid = entity_dict.pop("uid")
        
        return Entity(uid, **entity_dict)

class InvalidEntityTypeException(Exception):

    def __init__(self, data_type):
        self.data_type = data_type

        self.message = ("entity type '{}' is invalid").format(data_type)

        super().__init__(self.message)
