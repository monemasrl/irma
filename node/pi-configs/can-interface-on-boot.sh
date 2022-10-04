sudo systemctl enable --now systemd-networkd
sudo cp ./80-can.network /etc/systemd/network/
sudo systemctl restart systemd-networkd
