from machine import Pin

relay = Pin("LED",Pin.OUT)
relay.value(1)

while True:
    a = int(input("Enter the value : "))
    if(a==1):
        relay.value(1)
    elif(a==0):
        relay.value(0)
