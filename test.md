ab -k -c 5 -n 20000 'http://localhost:8080/' & \
ab -k -c 5 -n 2000 'http://localhost:8080/400' & \
ab -k -c 5 -n 3000 'http://localhost:8080/500' & \
ab -k -c 5 -n 5000 'http://localhost:8080/status/500' & \
ab -k -c 5 -n 5000 'http://localhost:8080/status/success'
#
