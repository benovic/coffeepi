def make_coffee():
   import app
   app.turn_on()
   app.log('brewing ...')
   app.sleep(60*30) # 3 miutes of brewing and holding warm
   app.log('stop holding warm and shutting off')
   app.turn_off()

def stop_coffee():
   import app
   app.turn_off()
   
