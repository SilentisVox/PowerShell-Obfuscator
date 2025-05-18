# PowerShell-Obfuscator

By far the hardest part of getting a malicious script to run on a target machine is evading AV.

```diff
- .\Script.ps1 : Operation did not complete successfully because the file contains a virus or potentially unwanted software.
```

Being able to leverage PowerShell for payload development is critical. But because the scripts can be read and easily flagged by AV, we want to go through and ensure that parts of the script are not "readable".

### **Setup**

```
git clone https://github.com/SilentisVox/PowerShell-Obfuscator.git
cd PowerShell-Obfuscator
pip install -r requirements.txt
python PowerShell-Obfuscator.py
```

## **Brief Explanation**

![Obfuscation](assets/Obfuscation.jpg)

### **String Based Indirection**

It's very easy to represent a string in PowerShell. With PowerShell's inherent ability to run strings as commands, methods, or properties, we can "Obfuscate" them as such.

```powershell
# Command string dereference.
Invoke-Expression "Get-Command"

# Method string derefernce.
"Hello, World!".("ToCharArray")()

# Property string dereference.
"Hello, World!".("Length")
```

Now the obfuscation techniques used for our string indirection are diverse, but easily understood.

#### Ordinal to Char to String

```powershell
# Take a list of oridinal values, cast them to chars, then using
# the join method from the string type, join them together.
$Ordinals = 72,101,108,108,111
$Chars    = $Ordinals | ForEach-Object { [Char] $_ }
$String   = [String]::Join("", $Chars)

# But will be represented as:
[string]::join("",(72,101,108,108,111|%{[char]$_}))
```

#### Ordinal to Char Concatenate

```powershell
# Direct ordinal values being cast to a char, then concatenated.
[char](72)+[char](101)+[char](108)+[char](108)+[char](111)
```

#### Random Indexing

```powershell
# Have a randomized list with needed chars, the indices needed to
# extract those chars, then use the string concatenate operator 
# "-Join" to join them.
$RandomString  = "plobSerlbH"
$RandomIndices = 9,5,7,1,2
$Chars         = $RandomString[$RandomIndices]
$String        = $Chars -Join ""

# But will be represented as:
"plobSerlbH"[9,5,7,1,2] -join ""
```

#### Environment Variable Char Extraction

```powershell
# Because of the methods in obtaining environment varaibles
# indices is fairly difficult, I will only show the end result.
$env:PSModulePath[130]+$env:PUBLIC[5]+$env:PSModulePath[50]+$env:ProgramFiles[13]+$env:ProgramFiles[5]
```

### **Case Randomization**

PowerShell has no "care" for a command, type, method, or property has randomized cases, it all will resolve.

Specifically for types, we will use this method, as we cannot use string dereferencing.

```powershell
# Ransomized case for a type.
[sYSteM.nET.socketS.TcPcLIENt]
```

### **Variable Rename Obfuscation**

To apply even more difficulty to reading our script, we will give random names to our variables. This will increase the incoherency.

```powershell
# Change from our typical readable variable names,
# to unreadable
$Hello            = "Hello"
$Sx8z5taC27HzrPY7 = "Hello"
```