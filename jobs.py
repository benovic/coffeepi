def make_coffee():
   import app
   app.turn_on()
   app.log('brewing ... sleeping')
   app.sleep(60) # 3 miutes for testing,  minute for brewing
   app.log('brewing ... waking up')
   app.turn_off()

def stop_coffee():
   import app
   app.turn_off()
   
