import os

class CommandHandler:
    def __init__(self, parser, objectconfig, targetedobjects, obfuscator, textassets) -> None:
        self.parser                     = parser
        self.objectconfig               = objectconfig
        self.targetedobjects            = targetedobjects
        self.obfuscator                 = obfuscator
        self.file_path                  = ""
        self.level                      = 5
        self.textassets                 = textassets
        self.commands                   = {
            ""                          : self.nothing,
            "help"                      : self.get_help,
            "clear"                     : self.clear,
            "exit"                      : self.exit_script,
            "load"                      : self.load_path,
            "level"                     : self.set_level,
            "run"                       : self.obfuscate,
            "save"                      : self.save_file
        }
        self.file_data                  = None

    def nothing(self) -> None:
        return

    def get_help(self) -> None:
        print(self.textassets.help_menu)

    def clear(self) -> None:
        self.textassets.flush()

    def exit_script(self) -> None:
        exit()

    def load_path(self) -> None:
        message                         = self.textassets.white("Input the path to the file.")
        print(message)
        path                            = input("> ")
        path_exists                     = os.path.exists(path)
        path_isfile                     = os.path.isfile(path)
        path_isreadable                 = os.access(path, os.R_OK)

        if not path_exists:
            error                       = self.textassets.red("Path does not exist!")
            print(error)
            return

        if not path_isfile:
            error                       = self.textassets.red("Path is not a file!")
            print(error)
            return

        if not path_isreadable:
            error                       = self.textassets.red("File is not readable!")
            print(error)
            return

        try:
            with open(path, "r") as file_buffer:
                self.file_data          = file_buffer.read()
        except:
            error                       = self.textassets.red("Failed to read file!")
            print(error)
            return

        print(self.textassets.success("Success!"))

    def set_level(self) -> None:
        message                         = self.textassets.white("Input the level of obfuscation. (1-5)")
        print(message)
        level_input                     = input("> ")
        level_list                      = []

        for level in range(1,6):
            level                       = str(level)
            level_list.append(level)

        if level_input not in level_list:
            error                       = self.textassets.red("Not a valid level!")
            print(error)
            return

        level                           = int(level_input)
        self.level                      = level
        print(self.textassets.success("Success!"))

    def obfuscate(self) -> None:
        parser                          = self.parser(
            obfuscator                  = self.obfuscator, 
            file_data                   = self.file_data, 
            level                       = self.level, 
            objectconfig                = self.objectconfig, 
            targetedobjects             = self.targetedobjects
        )
        objects                         = []

        for name, value in parser.objects.__dict__.items():
            objects.append(value)

        text                            = self.textassets.green("Formatting File.")
        drop_down                       = b"\x70\x25\x00\x25".decode("utf-16le")
        print(text)

        parser.delete_comments()
        parser.delete_empty()

        text                            = "{} Formatted File.".format(drop_down)
        print(text)

        text                            = self.textassets.blue("Finding Objects.")
        print(text)

        for object_ in objects:
            find_function               = object_.find
            items_found                 = find_function()
            text                        = "{} Found {} collective {}.".format(drop_down, items_found, object_.name)            
            print(text)

        text                            = self.textassets.purple("Replace Objects.")
        print(text)

        for object_ in objects:
            replace_function            = object_.replace
            items_replaced              = replace_function()
            text                        = "{} Replaced {} unique {}.".format(drop_down, items_replaced, object_.name)
            print(text)

        parser.squish()

        self.file_data                  = parser.file_data

    def save_file(self) -> None:
        current_directory               = os.getcwd()
        message                         = "Input path to save file. ({}\\.)".format(current_directory)
        print(message)
        path                            = input("> ")
        
        try:
            with open(path, "w") as file_buffer:
                file_buffer.write(self.file_data)
        except:
            error                       = self.textassets.red("Not a valid file path!")
            print(error)
            return

        print(self.textassets.success("Success!"))

    def read_input(self, user_input) -> None:
        if user_input not in self.commands:
            error                       = self.textassets.red("Command not recognized! > try 'help'")
            print(error)
            return

        self.commands[user_input]()