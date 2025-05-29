import re
import random
import dataclasses

@dataclasses.dataclass
class ObjectConfig:
    name                                : str
    pattern                             : re.Pattern
    held                                : list[str]
    find                                : object
    replace                             : object

@dataclasses.dataclass
class TargetedObjects:
    variables                           : ObjectConfig
    functions                           : ObjectConfig
    strings                             : ObjectConfig
    types                               : ObjectConfig
    inline_types                        : ObjectConfig
    methods                             : ObjectConfig
    attributes                          : ObjectConfig
    commands                            : ObjectConfig

class ObfuscationParser:
    def __init__(self, obfuscator, file_data, level, objectconfig: ObjectConfig, targetedobjects: TargetedObjects):
        self.obfuscator                 = obfuscator
        self.obfuscator_functions       = self.obfuscator.obfuscator_functions
        self.objects                    = None
        self.file_data                  = file_data
        self.level                      = level
        self.level_map                  = {
            1                           : 1,
            2                           : 2,
            3                           : 4,
            4                           : 6,
            5                           : 8
        }
        self.objectconfig               = objectconfig
        self.targetedobjects            = targetedobjects
        self.get_objects()

    def get_objects(self) -> None:
        object_names                    = [
            "variables",
            "functions",
            "strings",
            "types",
            "inline_types",
            "methods",
            "attributes",
            "commands"
        ]
        object_patterns                 = [
            r"\$[A-Za-z0-9_]+",
            r"(?i)(?:function)\s+([A-Za-z0-9\-]+)",
            r"(@\"[\s\S]*?\"@|@'[\s\S]*?'@|\"[^\"\r\n]*\"|'[^'\r\n]*')",
            r"\[[A-Za-z0-9.]+\]",
            r"(?i)(?:\b(?:New-Object|Add-Member)\b|-TypeName|-AssemblyName)\s+([A-Za-z0-9_\.\[\]]+)",
            r"((?:\.|::)[A-Za-z0-9](?:[A-Za-z0-9]*[A-Za-z0-9])?\()",
            r"(?<!\.)\.(?![A-Za-z0-9]+['\"\.\[\(\]])([A-Za-z0-9_]+)",
            r"(?<=[()[\]{};,|+\s])([A-Za-z][A-Za-z0-9]*-[A-Za-z0-9]+)(?=[()[\]{};,|+\s])"
        ]
        object_finds                    = [
            self.find_variables,
            self.find_functions,
            self.find_strings,
            self.find_types,
            self.find_inline_types,
            self.find_methods,
            self.find_attributes,
            self.find_commands
        ]
        object_replaces                 = [
            self.replace_variables,
            self.replace_functions,
            self.replace_strings,
            self.replace_types,
            self.replace_inline_types,
            self.replace_methods,
            self.replace_attributes,
            self.replace_commands
        ]
        object_count                    = self.level_map[self.level]
        object_configs                  = []
        
        for index in range(object_count):
            new_object                  = self.objectconfig(
                name                    = object_names    [index],
                pattern                 = object_patterns [index], 
                held                    = [],
                find                    = object_finds    [index], 
                replace                 = object_replaces [index]
            )
            object_configs.append(new_object)

        self.objects                    = self.targetedobjects(*object_configs)

    def delete_comments(self) -> None:
        multiline_pattern               = r"<#.*?#>"
        self.file_data                  = re.sub(multiline_pattern, "", self.file_data, flags=re.DOTALL)
        comment_pattern                 = r"#.*?\n"
        self.file_data                  = re.sub(comment_pattern, "\n", self.file_data)
        
    def delete_empty(self) -> None:
        empty_pattern                   = r"(?m)^[ \t]*\r?\n"
        self.file_data                  = re.sub(empty_pattern, "", self.file_data)

        file_lines                      = self.file_data.splitlines()
        file_formatted                  = []

        for line in file_lines:
            stripped_line               = line.strip()
            
            if not stripped_line:
                continue

            collapsed_line              = " ".join(stripped_line.split())
            file_formatted.append(collapsed_line)

        self.file_data                  = "\n".join(file_formatted)

    def find_variables(self) -> int:
        pattern                         = self.objects.variables.pattern
        variables_matched               = re.findall(pattern, self.file_data)
        self.objects.variables.held     = variables_matched
        results                         = len(variables_matched)

        return results

    def find_functions(self) -> int:
        pattern                         = self.objects.functions.pattern
        functions_matched               = re.findall(pattern, self.file_data)
        self.objects.functions.held     = functions_matched
        results                         = len(functions_matched)

        return results

    def find_strings(self) -> int:
        pattern                         = self.objects.strings.pattern
        strings_matched                 = re.findall(pattern, self.file_data)
        self.objects.strings.held       = strings_matched
        results                         = len(strings_matched)

        return results

    def find_types(self) -> int:
        pattern                         = self.objects.types.pattern
        types_matched                   = re.findall(pattern, self.file_data)
        self.objects.types.held         = types_matched
        results                         = len(types_matched)

        return results

    def find_inline_types(self) -> int:
        pattern                         = self.objects.inline_types.pattern
        inline_types_matched            = re.findall(pattern, self.file_data)
        self.objects.inline_types.held  = inline_types_matched
        results                         = len(inline_types_matched)

        return results

    def find_methods(self) -> int:
        pattern                         = self.objects.methods.pattern
        methods_matched                 = re.findall(pattern, self.file_data)
        self.objects.methods.held       = methods_matched
        results                         = len(methods_matched)

        return results

    def find_attributes(self) -> int:
        pattern                         = self.objects.attributes.pattern
        attributes_matched              = re.findall(pattern, self.file_data)
        self.objects.attributes.held    = attributes_matched
        results                         = len(attributes_matched)

        return results

    def find_commands(self) -> int:
        pattern                         = self.objects.commands.pattern
        commands_matched                = re.findall(pattern, self.file_data)
        self.objects.commands.held      = commands_matched
        results                         = len(commands_matched)

        return results

    def replace_variables(self) -> int:
        variables_matched               = self.objects.variables.held
        variables_unique                = set(variables_matched)
        variables_sorted                = sorted(variables_unique, key=len, reverse=True)
        os_variables                    = self.obfuscator.os_variables

        for variable_ in variables_sorted:
            variable_lower              = variable_.lower()
            variable_strip              = variable_lower[1:]

            if variable_strip in os_variables:
                continue

            random_variable             = "$" + self.obfuscator.random_variable()
            self.file_data              = self.file_data.replace(variable_, random_variable)

        results                         = len(variables_sorted)

        return results

    def replace_functions(self) -> int:
        functions_matched               = self.objects.functions.held
        functions_unique                = set(functions_matched)
        functions_sorted                = sorted(functions_unique, key=len, reverse=True)

        for function_ in functions_sorted:
            random_function             = self.obfuscator.random_variable()
            self.file_data              = self.file_data.replace(function_, random_function)

        results                         = len(functions_sorted)

        return results

    def replace_strings(self) -> int:
        strings_matched                 = self.objects.strings.held
        strings_unique                  = set(strings_matched)
        strings_sorted                  = sorted(strings_unique, key=len, reverse=True)
        exempt                          = ["''", '""']

        for string_ in strings_sorted:
            if string_ in exempt:
                continue

            if string_.startswith("@"):
                string_formatted        = string_[3:-3]
                random_function         = random.choice(self.obfuscator_functions[:3])
            else:
                string_formatted        = string_[1:-1]
                random_function         = random.choice(self.obfuscator_functions)

            randomized_string           = random_function(string_formatted)

            if "$" in string_:
                start                   = self.obfuscator.random_case("($ExecutionContext.InvokeCommand.ExpandString(")
                end                     = self.obfuscator.random_case("))")
                randomized_string       = start + randomized_string + end

            self.file_data              = self.file_data.replace(string_, randomized_string)

        results                         = len(strings_sorted)

        return results

    def replace_types(self) -> int:
        types_matched                   = self.objects.types.held
        types_unique                    = set(types_matched)
        types_sorted                    = sorted(types_unique, key=len, reverse=True)

        for type_ in types_sorted:
            random_type                 = self.obfuscator.random_case(type_)
            self.file_data              = self.file_data.replace(type_, random_type)

        results                         = len(types_sorted)

        return results

    def replace_inline_types(self) -> int:
        inline_types_matched            = self.objects.inline_types.held
        inline_types_unique             = set(inline_types_matched)
        inline_types_sorted             = sorted(inline_types_unique, key=len, reverse=True)

        for inline_type_ in inline_types_sorted:
            randomized_case             = self.obfuscator.random_case(inline_type_)
            random_function             = random.choice(self.obfuscator_functions)
            randomized_inline_type      = random_function(randomized_case)
            self.file_data              = self.file_data.replace(inline_type_, randomized_inline_type)

        results                         = len(inline_types_sorted)

        return results

    def replace_methods(self) -> int:
        methods_matched                 = self.objects.methods.held
        methods_unique                  = set(methods_matched)
        methods_sorted                  = sorted(methods_unique, key=len, reverse=True)

        for method_ in methods_sorted:
            if method_.startswith("."):
                reformat                = "."
                method_to_randomize     = method_[1:-1]
            else:
                reformat                = "::"
                method_to_randomize     = method_[2:-1]

            randomized_case             = self.obfuscator.random_case(method_to_randomize)
            random_function             = random.choice(self.obfuscator_functions)
            randomized_method           = random_function(randomized_case)
            randomized_method           = reformat + randomized_method + "("
            self.file_data              = self.file_data.replace(method_, randomized_method)

        results                         = len(methods_sorted)

        return results

    def replace_attributes(self) -> int:
        attributes_matched              = self.objects.attributes.held
        attributes_unique               = set(attributes_matched)
        attributes_sorted               = sorted(attributes_unique, key=len, reverse=True)

        for attribute_ in attributes_sorted:
            randomized_case             = self.obfuscator.random_case(attribute_)
            random_function             = random.choice(self.obfuscator_functions)
            attribute_                  = "." + attribute_
            randomized_attribute        = "." + random_function(randomized_case)
            self.file_data              = self.file_data.replace(attribute_, randomized_attribute)

        results                         = len(attributes_sorted)

        return results

    def replace_commands(self) -> int:
        commands_matched                = self.objects.commands.held
        commands_unique                 = set(commands_matched)
        commands_sorted                 = sorted(commands_unique, key=len, reverse=True)

        for command_ in commands_sorted:
            randomized_case             = self.obfuscator.random_case(command_)
            random_function             = random.choice(self.obfuscator_functions)
            randomized_command          = random_function(randomized_case)
            randomized_command          = "&" + randomized_command
            self.file_data              = self.file_data.replace(command_, randomized_command)

        results                         = len(commands_sorted)

        return results

    def get_param_start(self, index):
        while True:
            index                      += 1

            if self.file_data[index] == "(":
                return index

    def get_param_end(self, index):
        count                           = 1

        while True:
            index                      += 1

            if self.file_data[index] == "(":
                count                  += 1

            if self.file_data[index] == ")":
                count                  -= 1

            if count == 0:
                return index

    def squish(self) -> None:
        self.file_data                  = ";".join(self.file_data.splitlines())
        self.file_data                  = re.sub(r"\)[ ;]*\{",          "){",       self.file_data)
        self.file_data                  = re.sub(r"[; ]+\(",            "(",        self.file_data)
        self.file_data                  = re.sub(r"[; ]+\{",            "{",        self.file_data)
        self.file_data                  = re.sub(r"\([; ]+",            "(",        self.file_data)
        self.file_data                  = re.sub(r"\{[; ]+",            "{",        self.file_data)
        self.file_data                  = re.sub(r"[; ]+\)",            ")",        self.file_data)
        self.file_data                  = re.sub(r"[; ]+\}",            "}",        self.file_data)
        self.file_data                  = re.sub(r"[; ]+\}[; ]+",       "}",        self.file_data)
        self.file_data                  = re.sub(r"(?i)\}[; ]+else",    "}else",    self.file_data)
        self.file_data                  = re.sub(r"(?i)\}[; ]+elseif",  "}elseif",  self.file_data)
        self.file_data                  = re.sub(r"(?i)\}[; ]+catch",   "}catch",   self.file_data)
        self.file_data                  = re.sub(r"(?i)\}[; ]+finally", "}finally", self.file_data)
        self.file_data                  = re.sub(r"(?i)[; ]+param",     "param",    self.file_data)

        matches                         = re.finditer(r"(?i)\bparam\b", self.file_data)
        matches                         = reversed(list(matches))

        for match_ in matches:
            index                       = match_.start()
            param_start                 = self.get_param_start(index)
            param_end                   = self.get_param_end(param_start)
            param_block                 = self.file_data[index:param_end + 1]
            param_block                 = re.sub(r";", "", param_block)
            self.file_data              = self.file_data[:index] + param_block + self.file_data[param_end + 1:]

def test_parser():
    objectconfig                        = ObjectConfig
    targetedobjects                     = TargetedObjects

    with open("./payload/example3.ps1", "r", encoding="utf-8", errors="ignore") as file_buffer:
        file_data                       = file_buffer.read()

    parser                              = ObfuscationParser(Obfuscator(), file_data, 5, objectconfig, targetedobjects)

    parser.delete_comments()
    parser.delete_empty()

    parser.find_variables()
    parser.find_functions()
    parser.find_strings()
    parser.find_types()
    parser.find_inline_types()
    parser.find_methods()
    parser.find_attributes()
    parser.find_commands()

    parser.replace_variables()
    parser.replace_functions()
    parser.replace_strings()
    parser.replace_types()
    parser.replace_inline_types()
    parser.replace_methods()
    parser.replace_attributes()
    parser.replace_commands()

    parser.squish()

    print(parser.file_data)

if __name__ == "__main__":
    from Obfuscator import Obfuscator
    test_parser()