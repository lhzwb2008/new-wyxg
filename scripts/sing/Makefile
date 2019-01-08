CC = g++

# testcallso is a sample code to call libniao.so
testcallso: libniao.so testNiaoLib.cpp
	$(CC) testNiaoLib.cpp -L. libniao.so -o testcallso
