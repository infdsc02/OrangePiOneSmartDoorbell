# Smart Doorbell
Timbre inteligente utilizando una Orange Pi One. Cada vez que alguien llama a la puerta reproduce 
el sonido que se especifique en la configuración y, en caso de tener un Broker MQTT configurado, 
publica en un topic la fecha y hora a la que se ha producido la llamada.

El switch del timbre debe de ser conectado a utilizando una resistencia de pull-up (en mi caso utilicé una resistencia de 
10k) como se muestra en el siguiente esquema:

![Esquema electrico](https://github.com/infdsc02/OrangePiOneSmartDoorbell/blob/master/electronic_eschema/Esquema_Fritzing_bb.png?raw=true)

## Configuración
Plantilla del fichero de configuración que se debe de encontrar en 
"<path_del_proyecto>/data/cfg/conf.yaml":
```
logging:
  level: debug
  format: "%(asctime)s - [%(levelname)s] - %(processName)s : %(threadName)s - %(funcName)s : %(filename)s : %(lineno)d - %(message)s"

gpio:
  switch_pin: 10 # Pin físico al que se conecta el switch del timbre, si este valor no está
                 # se utiliza el pin 10 por defecto

# Si la conf de mqtt_broker no existe, no se lanzan eventos mqtt
mqtt:
  broker:
    host: # IP o hostname del broker MQTT
    port: # Puerto de escucha del broker MQTT
    user: # Puede ir en blanco en caso de que el broker no tenga autenticación
    passwd: # Puede ir en blanco en caso de que el broker no tenga autenticación
  pub_topic: # Nombre del topic en el que se publicará el evento cada vez que se toque el timbre

# Si no existe esta entrada utilizará los valores por defecto
# path = <path_del_proyecto>/data/sounds y volume = 0.5
audio:
  path: ./sounds # Path del fichero que se reproducirá cada vez que se pulse el timbre. En caso de
                 # ser una carpeta se seleccionará, de forma aleatoria, un fichero (.wav o .mp3) 
                 # cada vez que alguien toque el timbre. 
  volume: 1.0 # Valor entre 0 y 1

```