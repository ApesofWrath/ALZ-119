intsructions for running python script at boot:
open terminal and elevate to root using "sudo -i"
move rc-local.service into /etc/systemd/system
move rc.local into /etc
run commands in order: 
chmod +x /etc/rc.local
systemctl enable rc-local
systemctl start rc-local.service
Then run "systemctl status rc-local.service" and make sure output says service is active
