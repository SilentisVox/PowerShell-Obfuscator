from core.CommandHandler                import CommandHandler
from core.ObfuscationParser             import ObfuscationParser, ObjectConfig, TargetedObjects
from core.Obfuscator                    import Obfuscator
from core.TextAssets                    import TextAssets

def main():
    objectconfig                       = ObjectConfig
    targetedobjects                    = TargetedObjects
    parser                             = ObfuscationParser

    obfuscator                         = Obfuscator()
    textassets                         = TextAssets()

    print(textassets.banner)

    commandhandler                     = CommandHandler(
        parser                         = parser,
        objectconfig                   = objectconfig,
        targetedobjects                = targetedobjects,
        obfuscator                     = obfuscator,
        textassets                     = textassets
    )

    while True:
        try:
            user_input                  = input(textassets.prompt)
            commandhandler.read_input(user_input)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()