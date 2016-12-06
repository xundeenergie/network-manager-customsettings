# nm-defaultprinter

In NetworkManager vermisse ich die Funktion, pro Verbindung einen Standard-Drucker festlegen zu können, der in CUPS auch bei Aktivierung dieser Verbindung durch NetworkManager auch festgelegt wird.

Dieses Projekt fügt diese Funktion dem NetworkManager hinzu. Vorerst noch ohne graphisches UI.

## Konfiguration
Den Konfigurationsfiles der Netzwerkverbindungen sowie /etc/NetworkManager/NetworkManager.conf werden neue Sections mit dem Namen [custom] hinzugefügt. Da hinein kommen manuelle Veränderungen und Ergänzungen.

Im konkreten Fall ist das DefaultPrinter.

Ein DefaultPrinter-Eintrag entspricht der 2. Spalte der Ausgabe von lpstat -p und ist der CUPS-Druckername. Ein String ohne Leerzeichen!

Bsp:

[custom]
DefaultPrinter =  CUPS-PDF

## Setzen eines Defaultprinters, wenn keine Netzwerkverbindung besteht:
(Wird in /etc/NetworkManager/NetworkManager.conf geschrieben)
Damit immer ein Standarddrucker zur Verfügung stehen kann, empfiehlt es sich, cups-pdf zu installieren.
Der Drucker heißt dann z.B. "PDF"

/etc/NetworkManager/defaultprinter.py -S -p PDF

## Setzen eines Defaultprinters für eine system-connection
Verbindungen können mit mehreren Parametern identifiziert werden. Sowohl über den Filenamen der Verbindung in /etc/NetworkManager/system-connections/ als auch über die id oder die uuid im jeweiligen Konfigurations-File der Verbindung.

Wenn in einem Verbindungs-Konfigurations-File kein DefaultPrinter angegeben ist, wird jener aus der Datei NetworkManager.conf im nm-Config-Verzeichnis als Fallback genommen.

### Setzen mittels Filenamen
Das Python-Skript sucht den Dateinamen - so der Pfad relativ angegeben ist (ohne '/' am Beginn) im Verzeichnis /etc/NetworkManager/system-connections/, oder überprüft ob die Datei überhaupt existiert (wenn der Pfad absolut ist).

Als Beispiel sei der fiktive Wireless-Access-Point mit der ESSID "UPC123456" gewählt.
Der Drucker heißt "RICOH-SW-Drucker"

Enthält der Dateiname Leer- oder Sonderzeichen, so ist der Ausdruck in Anführungszeichen zu setzen.

/etc/NetworkManager/defaultprinter.py -S -p RICOH-SW-Drucker -f UPC123456

oder

/etc/NetworkManager/defaultprinter.py -S -p RICOH-SW-Drucker -f /etc/NetworkManager/system-connections/UPC123456

das führt zum selben Ergebnis, wenn das File existiert - es wird im Konfigurationsfile die selbe [custom]-Section eingefügt wie schon zuvor in NetworkManager.conf.

### Setzen mittels id der Verbindung
Meistens sind sowohl der Filename als auch die darin befindliche id einer Verbindung gleich. Daher gilt dieses Beispiel auch für die oben genannte Verbindung. Der Unterschied ist: es wird -i statt -f als Optionsschalter verwendet. 

/etc/NetworkManager/defaultprinter.py -S -p RICOH-SW-Drucker -i UPC123456

### Setzen mittels uuid der Verbindung:
Die UUID einer Verbindung kann man sich mit 

nmcli con show

anzeigen lassen. nur die UUID der momentan aktiven Verbindung mit:

nmclie -t -f UUID con show --active

Gesetzt wird der DefaultPrinter für eine Verbindung mittels UUID so:

/etc/NetworkManager/defaultprinter.py -S -p RICOH-SW-Drucker -u e7c17771-d689-47fa-a31f-6bd139d33ba0

### Setzen des selben Druckers für mehrere Verbindungen gleichzeitig:
Durch mehrfache Verwendung von -f, -u oder -i Optionenen (auch gemischt) kann für mehrere Verbindungen gleichzeitig der gleiche Drucker als Standarddrucker festgelegt werden:

/etc/NetworkManager/defaultprinter.py -S -p RICOH-SW-Drucker -u e7c17771-d689-47fa-a31f-6bd139d33ba0  -i "Mein WLAN" -f "LAN-Verbindung 1" 


## Löschen des DefaultPrinter-Eintrages:
Durch aufruf des Skriptes mit der Option -S ohne Angabe eines Druckers wir der Default-Printer-Eintrag im Konfig-File gelöscht.

Für den NetworkManager als Fallback:

/etc/NetworkManager/defaultprinter.py -S

und für eine einzelne Verbindung, wiederum mit den drei Möglichkeiten Filename, id und uuid:

/etc/NetworkManager/defaultprinter.py -S -u e7c17771-d689-47fa-a31f-6bd139d33ba0
/etc/NetworkManager/defaultprinter.py -S -i UPC123456
/etc/NetworkManager/defaultprinter.py -S -f /etc/NetworkManager/system-connections/UPC123456

## Festlegen des Standarddruckers in CUPS:
Die Option "-C" (wie Change-Printer) setzt den neuen Standarddrucker. mit Angabe einer Verbindung wird jener der in der Verbinung hinterlegt ist genommen. Ohne Verbindungsangabe kommt jener des NetworkManager-Fallbacks zum Zuge.

Diese Option wird vom Dispatcher-Skript verwendet!

/etc/NetworkManager/defaultprinter.py -C -i UPC123456

## Abfrage des Standarddruckers:
Die Option "-G" (wie Get-Printer) gibt lediglich den Namen des Druckers zurück.

Ausgabe des Fallback-Druckers:

/etc/NetworkManager/defaultprinter.py -G

und der Drucker der Verbindung "UPC123456"

/etc/NetworkManager/defaultprinter.py -G -u e7c17771-d689-47fa-a31f-6bd139d33ba0
/etc/NetworkManager/defaultprinter.py -G -i UPC123456
/etc/NetworkManager/defaultprinter.py -G -f /etc/NetworkManager/system-connections/UPC123456

Ist kein Drucker in einer Verbindung hinterlegt, so wird jener des NetworkManagers (aus NetworkManager.conf) genommen.

