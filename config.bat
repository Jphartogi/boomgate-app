@echo off
for /f "tokens=14" %%a in ('ipconfig ^| findstr IPv4') do set _IPaddr=%%a
echo IP is: %_IPaddr%

SET IP_LISTEN=%_IPaddr%
SET IP_HOST="127.0.0.1"

SET PORT_CONNECT_MASUK="5000"
SET PORT_CONNECT_KELUAR="5001"

SET PORT_LISTEN_MASUK="13820"
SET PORT_LISTEN_KELUAR="13821"

ECHO Showing current portproxy 
ECHO ==============================================
netsh interface portproxy show acmll
ECHO Deleting and resetting portproxy ....
netsh interface portproxy delete v4tov4 listenport=%PORT_LISTEN_MASUK% listenaddress=%IP_LISTEN%
netsh interface portproxy delete v4tov4 listenport=%PORT_LISTEN_KELUAR% listenaddress=%IP_LISTEN%
ECHO Showing portproxy after reset
ECHO ==============================================
netsh interface portproxy show all
ECHO adding port proxy ..
netsh interface portproxy add v4tov4 listenport=%PORT_LISTEN_MASUK% listenaddress=%IP_LISTEN% connectport=%PORT_CONNECT_MASUK% connectaddress=%IP_HOST%
netsh interface portproxy add v4tov4 listenport=%PORT_LISTEN_KELUAR% listenaddress=%IP_LISTEN% connectport=%PORT_CONNECT_KELUAR% connectaddress=%IP_HOST%
ECHO Showing portproxy after adding
ECHO ==============================================
netsh interface portproxy show all

ECHO disabling firewall..
ECHO ==============================================
netsh advfirewall set allprofiles state off

PAUSE