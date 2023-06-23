import uuid

from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect


from .game import Game

class SessionHandler:

    def __init__(self, session):
        self.session = session
        self.context = {}
        self.values = {}

        self.ACTIONS = { 'get'     : self.get_session,
                         'set'     : self.set_session,
                         'clear'   : self.clear_session,
                         'context' : self.add_context }

    def get_session(self, key, add_context):
        value = ''

        try:
            value = self.session[key]
        except:
            pass

        self.values[key] = value
        if add_context:
            self.context[key] = value

    def set_session(self, key, value, add_context):
        self.session[key] = value
        self.values[key] = value

        if add_context:
            self.context[key] = value

    def clear_session(self, key):
        self.session[key] = ''

    def add_context(self, key, value):
        self.context[key] = value

    def resolve(self, actions):
        for action in actions:
            action_cpy = action.copy()
            typ = action_cpy.pop(0)

            self.ACTIONS[typ](*action_cpy)

def set_game(game_controller, system, game):
    system = system.replace(':', '')
    game = game.replace(':', '')

    game_controller.set_game(system, game)

def set_default(session_handler, game_controller):
    data_types = game_controller.get_types()[1]
    actions = [ ['set', 'data_types', data_types, True],
                ['clear', 'detail_items'],
                ['clear', 'items'],
                ['get', 'system', True],
                ['get', 'game', True],
                ['get', 'alert', False],
                ['get', 'filter_string', False],
                ['get', 'filter_key', False],
                ['get', 'filter_value', False] ]

    session_handler.resolve(actions)

def get_details(session_handler, objects, detail_items):
    if objects:
        obj = objects[0]
        uid = obj.pop('uid')
        object_type = obj['data_type']

        dictionaries = {}
        lists = {}
        attributes = {}

        if 'items' in obj.keys():
            obj['item list'] = obj.pop('items')

        for name, item in obj.items():
            if type(item) is dict:
                dictionaries[name] = item
            elif type(item) is list:
                lists[name] = item
            else:
                attributes[name] = item

        item = {'uid'          :  uid,
                'attributes'   :  attributes,
                'lists'        :  lists,
                'dictionaries' :  dictionaries,
                'object_type'  :  object_type }

        detail_items.append(item)

def about(request):
    return render(request, 'about.html')

def index(request):
    game_controller = Game()
    data_types = game_controller.get_types()[1]

    session_handler = SessionHandler(request.session)
    
    actions = [ ['set', 'data_types', data_types, True],
                ['clear', 'detail_items'],
                ['clear', 'items'],
                ['get', 'system', False],
                ['get', 'game', False],
                ['get', 'alert', False],
                ['get', 'filter_string', False],
                ['get', 'filter_key', False],
                ['get', 'filter_value', False] ]

    session_handler.resolve(actions)
    values = session_handler.values

    if not request.user.is_authenticated:
        return render(request, 'about.html')

    actions = []

    filter_string = values['filter_string']
    if filter_string:
        if ':' in filter_string:
                filter_key, filter_value = filter_string.split(':')
        else:
            filter_key = 'name'
            filter_value = filter_string

    else:
        filter_key = values['filter_key']
        filter_value = values['filter_value']

    system, game = values['system'], values['game']
    if system and game:
        actions.append(['context', 'system', system])
        actions.append(['context', 'game', game])

        game_controller.set_game(system, game)

        items = []
        for data_type in data_types:
            obj_dicts = game_controller.find(data_type, '', '')

            for dictionary in obj_dicts:
                if filter_key and filter_value:
                    if filter_key == 'name':
                        filter_value = filter_value.lower()

                    try:
                        value = dictionary[filter_key]
                        print(value)

                        if filter_value in value:
                            items.append(dictionary)
                    except:
                        pass
            
                else:
                    items.append(dictionary)
        
        actions.append(['context', 'items', items])

    alert = values['alert']
    if alert:
        actions.append(['context', 'alert', alert])
        actions.append(['clear', 'alert'])
    
    actions.append(['clear', 'filter_string'])
    actions.append(['clear', 'filter_key'])
    actions.append(['clear', 'filter_value'])

    session_handler.resolve(actions)
    context = session_handler.context

    return render(request, 'index.html', context=context)

def new_game(request):
    if request.method == 'POST':
        system = None
        game = None

        try:
            system = request.POST['system']
            game = request.POST['game']
        except:
            pass

        if system and game:
            system = system.replace(':', '').lower()
            game = game.replace(':', '').lower()

            game_controller = Game()
            game_controller.set_game(system, game)
            
            request.session['system'] = system
            request.session['game'] = game

            request.session['alert'] = 'New Game Started'

        else:
            request.session['alert'] = 'New Game Failed'

        return HttpResponseRedirect(reverse('index'))

    elif request.method == 'GET':
        return render(request, 'new_game.html', None)
    
    return HttpResponseRedirect(reverse('index'))

def make_object(request):
    game_controller = Game()
    session_handler = SessionHandler(request.session)

    set_default(session_handler, game_controller)

    values = session_handler.values
    context = session_handler.context

    actions = [ ['get', 'detail_items', False],
                ['get', 'uid', False] ]
    session_handler.resolve(actions)

    values.update(session_handler.values)
    
    system = values['system']
    game = values['game']
    uid = values['uid']
    data_types = values['data_types']

    set_game(game_controller, system, game)

    if request.method == 'POST':

        if system and game:
            set_game(game_controller, system, game)

            try:
                name = request.POST['name'].lower()
                data_type = request.POST['data_type'].lower()
            except:
                name = ''
                data_type = ''

            if name and data_type:
                if data_type in data_types:
                    obj_dict = game_controller.make_obj(data_type, name=name)

                    if obj_dict:
                        actions = [['set', 'alert', 'Object Created', True]]
                    else:
                        actions = [['set', 'alert', 'Creation Failed', True]]

                    session_handler.resolve(actions)
                    return HttpResponseRedirect(reverse('index'))

        return HttpResponseRedirect(reverse('index'))

    elif request.method == 'GET':
        return render(request, 'make.html', context=context)

def modify_object(request):
    game_controller = Game()
    session_handler = SessionHandler(request.session)
    
    set_default(session_handler, game_controller)

    values = session_handler.values
    context = session_handler.context

    system = values['system']
    game = values['game']
    data_types = values['data_types']

    set_game(game_controller, system, game)

    detail_items = []

    if request.method == 'GET':
        uid = request.GET.get('uid')
        actions = []

        if uid and game and system:
            actions.append(['set', 'uid', uid, False])

            objects = game_controller.find(None, 'uid', uid)
            
            get_details(session_handler, objects, detail_items)
            data_type = detail_items[0]['object_type']
            actions.append(['set', 'data_type', data_type, False])

        actions.append(['context', 'detail_items', detail_items])
        session_handler.resolve(actions)

        context.update(session_handler.context)

        return render(request, 'modify.html', context=context)
    
    elif request.method == 'POST':
        post_data = dict(request.POST)
        print(post_data)

        obj_dict = {}
        
        obj_dict['name'] = post_data['name'][0]
        obj_dict['data_type'] = post_data['data_type'][0]

        actions = [ ['get', 'uid', False],
                    ['get', 'data_type', False] ]
        session_handler.resolve(actions)

        def check_string(string):
		  
            if isinstance(string, str) and string.isnumeric():
                return int(string)
            else:
                return string
        
        uid = session_handler.values['uid']
        data_type = session_handler.values['data_type']
       
        for key, value in post_data.items():
            data_context = key.split('.')

            if data_context[0] == 'attribute':
                variable = check_string(post_data[key][0])
                obj_dict[data_context[1]] = variable

            elif data_context[0] == 'list':
                if data_context[1] in obj_dict.keys():
                    variable = check_string(post_data[key])
                    obj_dict[data_context[1]] += variable
                else:
                    variable = check_string(post_data[key])
                    obj_dict[data_context[1]] = variable

            elif data_context[0] == 'dictionary':
                if data_context[1] in obj_dict.keys():
                    variable = check_string(post_data[key][0])
                    obj_dict[data_context[1]][data_context[2]] = variable
                else:
                    variable = check_string(post_data[key][0])
                    obj_dict[data_context[1]] = { data_context[2]: variable }

        game_controller.find(data_type, 'uid', uid)

        print(obj_dict)
        
        game_controller.delete_obj(uid)

        data_type = obj_dict.pop('data_type')
        new_obj = game_controller.make_obj(data_type, **obj_dict)
        game_controller.save_objs()

        uid = new_obj['uid']

        url = ("%s?uid=" + uid) % reverse('view')

        return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse('index'))

def delete_game(request):
    if request.method == 'POST':
        system = None
        game = None

        try:
            system = request.session['system']
            game = request.session['game']
        except:
            pass

        if system and game:
            status = Game.remove_game(system, game)
            
            if status:
                request.session['alert'] = 'Game Deleted'
                
                request.session['system'] = ''
                request.session['game'] = ''

            else:
                request.session['alert'] = 'Game Deletion Failed'
        
        return HttpResponseRedirect(reverse('index'))

    return HttpResponseRedirect(reverse('index'))

def select_game(request):
    databases = Game.list_games()

    if request.method == 'POST':
        try:
            if request.POST['system']:
                post_type = 'system'
        except:
            post_type = 'none'

        try:
            if request.POST['game']:
                post_type = 'game'
        except:
            pass

        if post_type == 'system':
            request.session['system'] = request.POST['system']
            request.session['new_game'] = 'true'

            return HttpResponseRedirect(request.path_info)

        elif post_type == 'game':
            request.session['game'] = request.POST['game']
            request.session['new_game'] = ''

            return HttpResponseRedirect(reverse('index'))

    elif request.method == 'GET':
        try:
            is_newgame = request.session['new_game']
        except:
            is_newgame = 'false'

        if is_newgame == 'true':
            games = []

            for database in databases:
                system, game = database.split(':')

                if system == request.session['system']:
                    games.append(game)
            
            context = {'games': games}
            return render(request, 'select_game.html', context=context)

        else:
            request.session['game'] = ''
            request.session['system'] = ''

            systems = []

            for database in databases:
                system = database.split(':')[0]

                if system not in systems:
                    systems.append(system)

            context = {'systems': systems}
            return render(request, 'select_game.html', context=context)

        return HttpResponseRedirect(reverse('index'))

def view(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')

        system = None
        game = None
        data_types = None

        items = None
        detail_items = None

        alert = None

        try:
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']
        except:
            pass

        try:
            detail_items = request.session['detail_items']
            if not detail_items:
                detail_items = []
        except:
            pass

        try:
            items = request.session['items']
            if not items:
                items = []
        except:
            pass

        try:
            alert = request.session['alert']
            print(alert)
        except:
            pass

        if uid and game and system:
            game_controller = Game()
            game_controller.set_game(system, game)

            objects = game_controller.find(None, 'uid', uid)

            if objects:
                obj = objects[0]
                uid = obj.pop('uid')
                object_type = obj['data_type']

                dictionaries = {}
                lists = {}
                attributes = {}

                if 'items' in obj.keys():
                    obj['item list'] = obj.pop('items')

                for name, item in obj.items():
                    if type(item) is dict:
                        dictionaries[name] = item
                    elif type(item) is list:
                        lists[name] = item
                    else:
                        attributes[name] = item

                item = {'uid'          :  uid,
                        'attributes'   :  attributes,
                        'lists'        :  lists,
                        'dictionaries' :  dictionaries,
                        'object_type'  :  object_type }

                detail_items.append(item)

                context = {'detail_items' :  detail_items,
                           'items'        :  items,
                           'game'         :  game,
                           'system'       :  system,
                           'data_types'   :  data_types}

                if alert:
                    context['alert'] = alert

                return render(request, 'view.html', context=context)
            

    return HttpResponseRedirect(reverse('index'))

def resolve(request):
    if request.method == 'POST':
        encounter_uid = None
        system = None
        game = None
        data_types = None

        try:
            encounter_uid = request.POST['encounter_uid']
            
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']

            game_controller = Game()
            game_controller.set_game(system, game)

            outcome, entities = game_controller.resolve(encounter_uid)
            game_controller.save_objs()

            request.session['outcome'] = outcome
            request.session['items'] = entities
            request.session['encounter_uid'] = encounter_uid

            return HttpResponseRedirect(request.path_info)
        except Exception as e:
            print(e)

    elif request.method == 'GET':
        system = None
        game = None
        data_types = None
        items = None
        outcome = None
        uid = None

        context = {}

        try:
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']

            items = request.session['items']
            outcome = request.session['outcome']
            
            uid = request.session['encounter_uid']

            if uid and game and system:
                game_controller = Game()
                game_controller.set_game(system, game)

                objects = game_controller.find(None, 'uid', uid)

                if objects:
                    obj = objects[0]
                    uid = obj.pop('uid')
                    object_type = obj['data_type']

                    dictionaries = {}
                    lists = {}
                    attributes = {}

                    if 'items' in obj.keys():
                        obj['item list'] = obj.pop('items')

                    for name, item in obj.items():
                        if type(item) is dict:
                            dictionaries[name] = item
                        elif type(item) is list:
                            lists[name] = item
                        else:
                            attributes[name] = item

                    detail_item = { 'attributes'    : attributes,
                                    'lists'         : lists,
                                    'dictionaries'  : dictionaries,
                                    'uid'           : uid,
                                    'object_type'   : object_type }
                    detail_items = []
                    detail_items.append(detail_item)
                    
                    request.session['detail_items'] = detail_items
                    context['detail_items'] = detail_items

                context['system'] = system
                context['game'] = game
                context['data_types'] = data_types
                context['items'] = items
                context['outcome'] = outcome

                context['alert'] = 'Encounter Resolved'
            
            return render(request, 'resolve.html', context=context)
        except Exception as e:
            print(e.message)

    return HttpResponseRedirect(reverse('index'))

def delete(request):
    if request.method == 'POST':
        uid = None
        system = None
        game = None
        data_types = None

        try:
            uid = request.POST['uid']
            
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']

            game_controller = Game()
            game_controller.set_game(system, game)
            
            game_controller.find(None, 'uid', uid)
            is_deleted = game_controller.delete_obj(uid)

            request.session['uid'] = ''

            if is_deleted:
                request.session['alert'] = "Object Deleted"
            else:
                request.session['alert'] = "Deletion Failed"

            return HttpResponseRedirect(request.path_info)
        except Exception as e:
            print(e)

    elif request.method == 'GET':
        system = None
        game = None
        data_types = None
        alert = None

        context = {}

        try:
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']
            
            alert = request.session['alert']
            request.session['alert'] = ''
            
            context['system'] = system
            context['game'] = game
            context['data_types'] = data_types
            context['alert'] = alert

            return render(request, 'index.html', context=context)
        except Exception as e:
            print(e.message)

    return HttpResponseRedirect(reverse('index'))

def copy(request):
    if request.method == 'POST':
        uid = None
        system = None
        game = None
        data_types = None

        try:
            uid = request.POST['uid']
            request.session['uid'] = uid
            
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']

            game_controller = Game()
            game_controller.set_game(system, game)
            
            obj_copy = game_controller.copy_obj(uid)
            game_controller.save_objs()

            if obj_copy:
                request.session['alert'] = "Object Copied"
            else:
                request.session['alert'] = "Copy Failed"

            return HttpResponseRedirect(request.path_info)
        except Exception as e:
            print(e)

    elif request.method == 'GET':
        system = None
        game = None
        data_types = None
        alert = None

        context = {}

        try:
            system = request.session['system']
            game = request.session['game']
            data_types = request.session['data_types']

            uid = request.session['uid']
            request.session['uid'] = ''
            
            alert = request.session['alert']
            request.session['alert'] = ''

            context['alert'] = alert

            context['system'] = system
            context['game'] = game
            context['data_types'] = data_types

            if uid and game and system:
                game_controller = Game()
                game_controller.set_game(system, game)

                objects = game_controller.find(None, 'uid', uid)
                items = []

                if objects:
                    obj = objects[0]
                    uid = obj.pop('uid')
                    object_type = obj['data_type']

                    dictionaries = {}
                    lists = {}
                    attributes = {}

                    if 'items' in obj.keys():
                        obj['item list'] = obj.pop('items')

                    for name, item in obj.items():
                        if type(item) is dict:
                            dictionaries[name] = item
                        elif type(item) is list:
                            lists[name] = item
                        else:
                            attributes[name] = item
                    
                    item = {'attributes'   : attributes,
                            'lists'        : lists,
                            'dictionaries' : dictionaries,
                            'uid'          : uid,
                            'object_type'  : object_type }
                    items.append(item)
                    print(items)

                    context['detail_items'] = items

            return render(request, 'view.html', context=context)
        except Exception as e:
            print(e.message)

    return HttpResponseRedirect(reverse('index'))


def filter(request):
    if request.method == 'POST':
        filter_key = None
        filter_value = None
        
        try:
            request.session['filter_key'] = request.POST['filter_key']
            request.session['filter_value'] = request.POST['filter_value']
        except:
            pass

        try:
            request.session['filter_string'] = request.POST['filter_string']
        except:
            pass

        return HttpResponseRedirect(reverse('index'))
