#HOST=pi-atari.lan
HOST=198.0.0.24
rsync -avz --exclude "__history" --exclude "*~" --exclude "*.gif" --exclude "*.JPG" -e ssh . pi@$HOST:/home/pi/chronograph/
