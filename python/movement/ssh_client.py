import paramiko

def stuur_coordinaten(x, y):

    # Gebruikersnaam en wachtwoord voor SSH
    gebruikersnaam = "sjonnie"
    wachtwoord = "sjon"

    # Verbind met de SSH-server
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Dit is handig als de server nog niet is toegevoegd aan known_hosts
    ssh_client.connect("141.252.29.47", username=gebruikersnaam, password=wachtwoord)

    # Stuur de coördinaten naar de server als een commando
    commando = f"{x},{y}"
    stdin, stdout, stderr = ssh_client.exec_command(commando)

    # Lees de uitvoer (indien nodig)
    output = stdout.read().decode("utf-8")
    print(output)

    # Sluit de SSH-verbinding
    ssh_client.close()

# Voorbeeldcoördinaten
x_coord = 10
y_coord = 20


