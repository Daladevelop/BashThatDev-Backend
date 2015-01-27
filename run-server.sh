#!/bin/bash
echo "Visit http://moosegame.jump to play the game"
vagrant ssh -c "cd /home/server && screen python ws.py" 
