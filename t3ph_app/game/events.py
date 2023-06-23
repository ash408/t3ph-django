
import random


class Effect():

    set_effct = {'set' : lambda a,b : b}
    add_effct = {'add' : lambda a,b : a + b}
    sub_effct = {'sub' : lambda a,b : a - b}

    TYPES = set_effct | add_effct | sub_effct

    def __init__(self, **kwargs):
        self.target = kwargs['target']
        self.e_type = kwargs['e_type']
        self.resource = kwargs['resource']
        self.amount = kwargs['amount']

        if self.e_type not in Effect.TYPES:
            raise InvalidEffectException(self.e_type)

    def get_inputs(self):
        e_dict = self.__dict__
        inputs = set()

        for key in e_dict.keys():
            if type(e_dict[key]) is str and 'input' in e_dict[key]:
                inputs.add(e_dict[key])

        return inputs

    def replace_inputs(self, inputs):
        e_dict = self.__dict__

        for key in e_dict.keys():
            for inpt in inputs.keys():
                if e_dict[key] == inpt:
                    e_dict[key] = inputs[inpt]

    def apply(self, entity):
        ent_resource_amnt = 0

        if hasattr(entity, 'resources'):
            if self.resource in entity.resources.keys():
                ent_resource_amnt = entity.resources[self.resource]
        else:
            entity.resources = {}

        func = Effect.TYPES[self.e_type]
        entity.resources[self.resource] = func(ent_resource_amnt, self.amount)


class Outcomes(dict):

    __slots__ = ()
    def __init__(self, outcome_dict = None):
        super().__init__()
        
        if outcome_dict:
            for key in outcome_dict.keys():
                self[key] = outcome_dict[key]

    def __setitem__(self, key, item):

        if type(key) is not str:
            raise InvalidOutcomeException('key')
        elif type(item) is not int:
            raise InvalidOutcomeException('item')
        elif item < 0:
            item = 0

        return super(Outcomes, self).__setitem__(key, item)
    
    def __get_roll(self):
        total = sum(self.values())
        roll = random.randint(1, total)

        return roll

    def resolve(self):
        roll = self.__get_roll()

        for outcome in self.keys():
            chance = self[outcome]

            if roll <= chance:
                return outcome
                
            else:
                roll -= chance

    def chances(self):
        chance_dict = {}
        max_chance = sum(self.values())

        for outcome in self.keys():
            percentage = (self[outcome] / max_chance) * 100
            chance_dict[outcome] = round(percentage)

        return chance_dict

    def increase_chance(self, target_outcome, amount=1):
        if amount < 1:
            amount = 1
            
        for _ in range(amount):
            modification_list = []
            highest_chance = 0

            for outcome in self.keys():
                test_outcomes = Outcomes(self.copy())

                if outcome == target_outcome:
                    test_outcomes[outcome] += 1
                else:
                    test_outcomes[outcome] -= 1

                chances = test_outcomes.chances()
                outcome_chance = chances[outcome]

                if outcome_chance > highest_chance:
                    highest_chance = outcome_chance

                modification_list.append([outcome_chance, test_outcomes])
        
            for item in modification_list:
                chance = item[0]
                new_outcomes = item[1]

                if chance == highest_chance:
                    for key in new_outcomes.keys():
                        self[key] = new_outcomes[key]


class Encounter():
    #potential kwargs: tags, effects, outcomes

    #effects = list of dictionaries with keys of target (target uid), e_type (add, set, remove),
    #   resource to be altered, and amount (int more or equal to 0) to alter it by

    #outcomes = dictionary with key of encounter uid and value of roll chance

    def __init__(self, uid, name='unnamed_encounter', **kwargs):
        self.uid = uid
        self.name = name
       
        effects = []
        outcomes_dict = {}

        params = kwargs.copy()
        for key in params.keys():
            if 'effect' in key:
                effect_dict = kwargs.pop(key)
                
                effect = Effect(**effect_dict)
                effects.append(effect)

                self.effects = effects

            if 'outcomes' in key:
                outcome = kwargs.pop(key)
                outcomes_dict.update(outcome) 
                self.outcomes = Outcomes(outcomes_dict)

        self.__dict__.update(kwargs)

    def get_inputs(self):
        inputs = None

        if hasattr(self, 'effects'):
            inputs = set()
            effects = self.effects

            for effect in effects:
                inputs.update(effect.get_inputs())
        else:
            return None

        return inputs

    def get_entities(self):
        entity_uids = None

        if hasattr(self, 'effects'):
            entity_uids = set()
            effects = self.effects

            for effect in effects:
                entity = effect.target

                if 'input' not in entity:
                    entity_uids.add(entity)

        return entity_uids

    def resolve(self, entities = None, **inputs):
        outcome = None
        
        if entities and hasattr(self, 'effects'):
            self.__resolve_effects(entities, inputs)
        
        if hasattr(self, 'outcomes') and self.outcomes:
            outcome = self.outcomes.resolve()

        return outcome

    def __has_inputs(self, entities, inputs):
        needed_inputs = self.get_inputs()
        entity_uids = set()

        for entity in entities:
            entity_uids.add(entity.uid)

        for key in inputs.keys():
            if key not in needed_inputs or inputs[key] not in entity_uids:
                return False
            else:
                needed_inputs.remove(key)
        
        if len(needed_inputs) == 0:
            return True
        else:
            return False

    def __has_entities(self, entities):
        needed_entity_uids = self.get_entities()
        check_entity_uids = set()
        
        
        for entity in entities:
            check_entity_uids.add(entity.uid)

        return needed_entity_uids == check_entity_uids

    def __replace_inputs(self, inputs, effects):
        for effect in effects:
            effect.replace_inputs(inputs)
        return effects

    def __resolve_effects(self, entities, inputs):
        effects = self.effects.copy()

        if self.get_inputs():
            effects = self.__replace_inputs(inputs, effects)

        if self.__has_entities(entities):
            for effect in effects:
                entity = None
                for test_entity in entities:
                    if test_entity.uid == effect.target:
                        entity = test_entity

                if entity == None:
                    raise NoTargetException(effect.target, self.uid)
                
                effect.apply(entity)

    def __str__(self):
        return str(self.name)

    def to_dict(self):
        encounter_dict = self.__dict__.copy()
        
        if 'outcomes' in encounter_dict:
            outcomes = encounter_dict.pop('outcomes')
            encounter_dict['outcomes'] = dict(outcomes)

            chances = outcomes.chances()
            encounter_dict['chances'] = chances

        if 'effects' in encounter_dict:
            effects_dict = {}
            effects = encounter_dict.pop('effects')
            
            num = 1
            for effect in effects:
                effect_key = 'effect' + str(num)
                encounter_dict[effect_key] = effect.__dict__.copy()
                num += 1

        return encounter_dict


    def from_dict(encntr_dict):
        encntr_dict = encntr_dict.copy()
        uid = encntr_dict.pop('uid')

        return Encounter(uid, **encntr_dict)


class InvalidEffectException(Exception):

    def __init__(self, effect):
        self.effect = effect

        self.message = ("effect '{}' is not valid").format(effect)

        super().__init__(self.message)


class InvalidOutcomeException(Exception):
    
    def __init__(self, value_type):
        self.value_type = value_type

        if self.value_type == 'key':
            self.message = 'outcome key must be a string'
        else:
            self.message = 'outcome value must be an integer'

        super().__init__(self.message)


class NoTargetException(Exception):

    def __init__(self, t_uid, e_uid):
        self.t_uid = t_uid
        self.e_uid = e_uid

        self.message = ("no target with uid '{}' found " + 
                        "when resolving encounter '{}'").format(t_uid, e_uid)

        super().__init__(self.message)
