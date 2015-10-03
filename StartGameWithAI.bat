@ECHO OFF

start runserver -n 1

timeout 4 > NUL

start runclient