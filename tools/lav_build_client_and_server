rm -r ./build*
make sdl -e FLAGS="-ggdb -DIS_SERVER"
mv build build_server
make sdl -e FLAGS="-ggdb"
mv build build_client
rm compile_commands.json
ln -s ./build_client/sdl/compile_commands.json ./
