
import sys
import inspect

from game import Game


class IO_Handler():

    def __init__(self, commands):
        self.commands = commands
        self.commands['help'] = self.output_help
        self.commands['quit'] = self.prompt_exit

    def prompt_command(self):
        command = ''

        while not command:
            command = Text_Menu.get_input('Command [HELP for list]: ')
            command = command.strip().lower()

            if command not in commands.keys():
                command = ''

        return command
        
    def output_help(self):
        commands = list(self.commands.keys())
        out = Text_Menu.format_list('commands', commands)
        
        Text_Menu.output(' ')
        Text_Menu.output(out)
    
    def get_params(self, function):
        try:
            sig = inspect.signature(function)
        except ValueError:
            return None

        args = list(sig.parameters)
        params = {}
        
        if args:
            Text_Menu.output(' ')
        
        for arg in args:
            if 'list' in arg:
                a_list = Text_Menu.prompt_list(arg)
                params[arg] = a_list

            elif arg == 'kwargs':
                obj_dict = Text_Menu.prompt_obj_dict()
                params[arg] = obj_dict

            else:
                value = Text_Menu.prompt_value(arg)
                params[arg] = value
       
        return params

    def check_command(self, command):
        commands = self.commands

        for check_command in commands.keys():
            if check_command == command:
                function = commands[command]
                params = self.get_params(function)
                    
                if params:
                    if 'kwargs' in params.keys():
                        kwargs = params.pop('kwargs')
                        out = function(**params, **kwargs)

                    else:
                        out = function(**params)
                else:
                    out = function()
                
                if out or type(out) == bool:
                    Text_Menu.output(out)

    def prompt_exit(self):
        inpt = Text_Menu.get_input('\n\nWould you like to quit? [Y/N]: ')
        inpt = inpt.lower()

        if inpt[0] == 'y':
            Text_Menu.output('\nSaving game...')
            self.check_command('save')
            Text_Menu.output(' ')

            sys.exit()

if __name__ == '__main__':
    game = Game()
    commands = game.commands
    handler = IO_Handler(commands)

    while True:
        command = None

        try:
            Text_Menu.output(' ')
            command = handler.prompt_command()
        except KeyboardInterrupt:
            handler.prompt_exit()
        
        if command:
            try:
                handler.check_command(command)
            except KeyboardInterrupt:
                Text_Menu.output(' ')
