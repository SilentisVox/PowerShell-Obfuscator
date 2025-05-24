import os

class TextAssets:
    def __init__(self) -> None:
        self.banner                     = f"""
    ____                          _____ __         ____    
   / __ \____ _      _____  _____/ ___// /_  ___  / / /    
  / /_/ / __ \ | /| / / _ \/ ___/\__ \/ __ \/ _ \/ / /_____
 / ____/ /_/ / |/ |/ /  __/ /   ___/ / / / /  __/ / /_____/
/_/____\____/|__/|__/\___/_/   /____/_/ /_/\___/_/_/       
  / __ \/ /_  / __/_  ________________ _/ /_____  _____    
 / / / / __ \/ /_/ / / / ___/ ___/ __ `/ __/ __ \/ ___/    
/ /_/ / /_/ / __/ /_/ (__  ) /__/ /_/ / /_/ /_/ / /        
\____/_.___/_/  \__,_/____/\___/\__,_/\__/\____/_/ 

      {self.white("[!] https://github.com/SilentisVox")}
  {self.red("[!] This tool is for educational purposes only.")}
"""
        self.banner_colors              = [
            (0, 132, 255),
            (0, 127, 250),
            (0, 123, 246),
            (0, 119, 241),
            (0, 115, 237),
            (0, 111, 232),
            (0, 107, 228),
            (0, 103, 223),
            (0, 99, 219),
            (0, 95, 214),
            (0, 91, 210),
            (0, 87, 205),
            (0, 83, 201),
            (0, 79, 196)
        ]
        self.apply_gradient()
        self.prompt                     = self.white(">>> ")
        self.plus                       = self.blue("[+]")
        self.help_menu                  = f"""

    {self.plus} help   ::  Prints this menu.
    {self.plus} clear  ::  Clears the terminal.
    {self.plus} exit   ::  Exits the script.
    {self.plus} load   ::  Sets the file path.
    {self.plus} level  ::  Sets the level of obfuscation.
    {self.plus} run    ::  Runs obfuscation.
    {self.plus} save   ::  Saves the file.

"""
    self.success                        = self.green("Success!")

    def apply_gradient(self) -> None:
        text_lines                      = self.banner.split("\n")
        text_length                     = len(text_lines)
        lines_and_colors                = []

        for index in range(text_length):
            line                        = text_lines[index]
            color                       = self.banner_colors[index]
            line_and_color              = (line, color)
            lines_and_colors.append(line_and_color)

        colored_text                    = []

        for line, color in lines_and_colors:
            color_code                  = "\x1b[38;2;{};{};{}m".format(color[0], color[1], color[2])
            end                         = "\x1b[0m"
            colored_line                = color_code + line + end
            colored_text.append(colored_line)

        self.banner                     = "\n".join(colored_text)

    def bold(self, text) -> str:
        return "\033[1m{}\033[0m".format(text)

    def underline(selft, text) -> str:
        return "\033[4m{}\033[0m".format(text)

    def white(self, text) -> str:
        return "\x1b[38;2;255;255;255m{}\x1b[0m".format(text)

    def red(self, text) -> str:
        return "\x1b[38;2;237;151;152m{}\x1b[0m".format(text)
    
    def green(self, text) -> str:
        return "\x1b[38;2;132;207;137m{}\x1b[0m".format(text)

    def blue(self, text) -> str:
        return "\x1b[38;2;153;225;245m{}\x1b[0m".format(text)

    def purple(self, text) -> str:
        return "\x1b[38;2;244;139;249m{}\x1b[0m".format(text)

    def flush(self) -> None:
        os.system('cls')