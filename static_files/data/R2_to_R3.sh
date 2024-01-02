sudo apt-get install -y sshpass

# send the r2 xml to windows vm
sshpass -p '{{VM_PS}}' scp -o StrictHostKeyChecking=no $1/$3 administrator@{{VM_HOST}}:C:/Users/Administrator/Desktop/BFC1/r2
# batch file in the windows vm
sshpass -p '{{VM_PS}}' ssh -o StrictHostKeyChecking=no administrator@{{VM_HOST}} 'C:/Users/Administrator/Desktop/R3.bat'
# copy generated R3 xml
sshpass -p '{{VM_PS}}' scp -o StrictHostKeyChecking=no administrator@{{VM_HOST}}:C:/Users/Administrator/Desktop/BFC1/r3/$3 $2/$3