if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi

pkill -f chronograph.py

/usr/local/bin/pigpiod -s 2 || echo "failed to install pgpiod -- already installed?"

cd /home/pi/chronograph

#LOG=/dev/null
LOG=/tmp/chronograph.log

su - pi -c "bash -c \"cd /home/pi/chronograph && nohup python /home/pi/chronograph/chronograph.py >> $LOG 2>&1 &\""
