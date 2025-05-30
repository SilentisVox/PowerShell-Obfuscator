import os
import random

class Obfuscator:
    def __init__(self) -> None:
        self.obfuscator_functions       = [
            self.numbers_to_characters_to_string,
            self.numbers_to_character_concatenate,
            self.numbers_to_character_concatenate_math,
            self.random_string_to_string,
            self.environment_variables_to_string
        ]
        self.characters                 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        self.printable                  = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ "
        self.os_variables               = [
            "answers",
            "args",
            "confirmpreference",
            "consolefilename",
            "debugpreference",
            "error",
            "erroractionpreference",
            "errorview",
            "executioncontext",
            "false",
            "formatenumerationlimit",
            "guesses",
            "home",
            "host",
            "informationpreference",
            "input",
            "lastexitcode",
            "maximumaliascount",
            "maximumdrivecount",
            "maximumerrorcount",
            "maximumfunctioncount",
            "maximumhistorycount",
            "maximumvariablecount",
            "myinvocation",
            "nestedpromptlevel",
            "null",
            "outputencoding",
            "pid",
            "profile",
            "profile_dir",
            "progresspreference",
            "psboundparameters",
            "pscommandpath",
            "psculture",
            "psdefaultparametervalues",
            "psedition",
            "psemailserver",
            "pshome",
            "psscriptroot",
            "pssessionapplicationname",
            "pssessionconfigurationname",
            "pssessionoption",
            "psuiculture",
            "psversiontable",
            "pwd",
            "shellid",
            "stacktrace",
            "true",
            "verbosepreference",
            "warningpreference",
            "whatifpreference"
        ]
        self.environment_variables      = [
            "ALLUSERSPROFILE",
            "CommonProgramFiles",
            "CommonProgramW6432",
            "ComSpec",
            "DriverData",
            "ProgramData",
            "ProgramFiles",
            "ProgramW6432",
            "PUBLIC",
            "SystemDrive",
            "SystemRoot",
            "windir"
        ]
        self.environment_variables_map  = {}
        self.get_environment_map()

    def add_character_index(self, character, variable, index) -> None:
        if character not in self.environment_variables_map:
            self.environment_variables_map[character] = {variable: [index]}
        elif variable not in self.environment_variables_map[character]:
            self.environment_variables_map[character][variable] = [index]
        else:
            self.environment_variables_map[character][variable].append(index)

    def process_environment_variable(self, variable) -> None:
        value                           = os.getenv(variable)
        for index, character in enumerate(value):
            if character in self.printable:
                self.add_character_index(character, variable, index)

    def get_environment_map(self) -> None:
        for variable in self.environment_variables:
            self.process_environment_variable(variable)

    def random_variable(self) -> str:
        variable_length                 = random.randint(1, 24)
        random_string                   = ""

        for iteration in range(variable_length):
            random_character            = random.choice(self.characters)
            random_string              += random_character

        return random_string

    def random_case(self, input_string: str) -> str:
        random_case_string              = ""

        for character in input_string:
            random_method               = random.choice([str.upper, str.lower])
            random_case_character       = random_method(character)
            random_case_string         += random_case_character

        return random_case_string

    def numbers_to_characters_to_string(self, input_string: str) -> str:
        string_ordinals                 = []

        for character in input_string:
            character_ordinal           = ord(character)
            string_ordinal              = str(character_ordinal)
            string_ordinals.append(string_ordinal)

        string_ordinals_list            = ",".join(string_ordinals)
        obfuscated_string               = "([string]::join('', ( ( {}".format(string_ordinals_list) + " ) |%{$_}|%{ ([char][int] $_)})) |%{$_}| % {$_})"

        return obfuscated_string

    def numbers_to_character_concatenate(self, input_string: str) -> str:
        obfuscated_characters           = []

        for character in input_string:
            character_ordinal           = ord(character)
            string_ordinal              = str(character_ordinal)
            obfuscated_character        = "[char]({})".format(string_ordinal)
            obfuscated_characters.append(obfuscated_character)

        obfuscated_character_string     = "+".join(obfuscated_characters)
        obfuscated_string               = "({})".format(obfuscated_character_string)

        return obfuscated_string

    def numbers_to_character_concatenate_math(self, input_string: str) -> str:
        obfuscated_characters           = []
    
        for character in input_string:
            random_number               = random.randint(1, 99)
            random_number_string        = str(random_number)
            operators                   = [("+", "-"), ("*", "/")]
            random_operator_set         = random.choice(operators)
            character_ordinal           = ord(character)
            string_ordinal              = str(character_ordinal)
            obfuscated_math             = random_number_string + random_operator_set[0] + string_ordinal + random_operator_set[1] + random_number_string
            obfuscated_character        = "([char]({}".format(obfuscated_math) + ")|%{$_}| % {$_} |%{$_})"
            obfuscated_characters.append(obfuscated_character)

        obfuscated_character_string     = "+".join(obfuscated_characters)
        obfuscated_string               = "({})".format(obfuscated_character_string)
        
        return obfuscated_string

    def random_string_to_string(self, input_string: str) -> str:
        input_string_length             = len(input_string)
        characters_needed               = input_string_length + 20
        randomized_characters           = [""] * characters_needed
        all_indices                     = range(characters_needed)
        randomized_indices              = random.sample(all_indices, k=characters_needed)
        indices_used                    = []
        
        for character in input_string:
            randomized_index            = randomized_indices[0]
            randomized_characters[randomized_index] = character
            randomized_index_string     = str(randomized_index)
            indices_used.append(randomized_index_string)
            del randomized_indices[0]
    
        for index, item in enumerate(randomized_characters):
            if not item:
                random_character        = random.choice(self.characters)
                randomized_characters[index] = random_character

        randomized_string               = "".join(randomized_characters)
        randomized_indices_string       = ",".join(indices_used)
        obfuscated_string               = "('{}'[{}".format(randomized_string, randomized_indices_string) + "] -join '' |%{$_}| % {$_})"

        return obfuscated_string

    def environment_variables_to_string(self, input_string: str) -> str:
        environment_variables           = []

        for character in input_string:
            if character in self.environment_variables_map:
                possible_dictionaries   = self.environment_variables_map[character]
                possible_variables_keys = possible_dictionaries.keys()
                possible_variables      = list(possible_variables_keys)
                chosen_variable         = random.choice(possible_variables)
                possible_indices        = possible_dictionaries[chosen_variable]
                chosen_index            = random.choice(possible_indices)
                chosen_index_string     = str(chosen_index)
                obfuscated_character    = "$env:{}[{}]".format(chosen_variable, chosen_index_string)
                environment_variables.append(obfuscated_character)
            else:
                other_functions         = [
                    self.numbers_to_characters_to_string, 
                    self.numbers_to_character_concatenate, 
                    self.numbers_to_character_concatenate_math, 
                    self.random_string_to_string
                ]
                other_function          = random.choice(other_functions)
                obfuscated_character    = other_function(character)
                environment_variables.append(obfuscated_character)

        obfuscated_characters           = "+".join(environment_variables)
        obfuscated_string               = "({})".format(obfuscated_characters)

        return obfuscated_string

    def final_pass(self, input_string: str) -> str:
        final_data_list                 = []

        for character in input_string:
            value                       = ord(character)
            value_string                = str(value)
            final_data_list.append(value_string)

        formatted_data                  = ",".join(final_data_list)
        obfuscated_string               = "([string]::join('',(({}".format(formatted_data) + ")|%{[char]$_})))|invoke-expression"

        return obfuscated_string

def test_obfuscation():
    obfuscator                          = Obfuscator()

    string_to_obfuscate                 = "[System.Net.Sockets.TCPClient]"

    random_variable                     = obfuscator.random_variable()
    random_type                         = obfuscator.random_case(string_to_obfuscate)
    random_string1                      = obfuscator.random_string_to_string(string_to_obfuscate)
    random_string2                      = obfuscator.numbers_to_character_concatenate(string_to_obfuscate)
    random_string3                      = obfuscator.numbers_to_character_concatenate_math(string_to_obfuscate)
    random_string4                      = obfuscator.environment_variables_to_string(string_to_obfuscate)

    print(random_variable)
    print(random_type)
    print(random_string1)
    print(random_string2)
    print(random_string3)
    print(random_string4)

if __name__ == "__main__":
    test_obfuscation()