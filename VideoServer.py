import cv2, socket, numpy, pickle
s=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
ip=""
port=6666
s.bind((ip,port))
while True:
    x=s.recvfrom(1000000)
    image_arr = np.frombuffer(x,np.uint8)
    image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
    if type(image) is type(None):
        pass
    else:
        cv2.imshow("Video stream", image)
        cv2.waitKey(1)
    # clientip = x[1][0]
    # data=x[0]
    # print(data)
    # data=pickle.loads(data)
    # print(type(data))
    # data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    # cv2.imshow('server', data) #to open image
    # if cv2.waitKey(10) == 13:
    #     break
cv2.destroyAllWindows()