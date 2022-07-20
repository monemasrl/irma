#include <ESP32_LoRaWAN.h>
#include "Arduino.h"


/*license for Heltec ESP32 LoRaWan, quary your ChipID relevant license: http://resource.heltec.cn/search */
uint32_t  license[4] = {0xD5397DF0, 0x8573F814, 0x7A38C73D, 0x48E68607};
/* OTAA para*/
uint8_t DevEui[] = { 0x22, 0x32, 0x33, 0x00, 0x00, 0x88, 0x88, 0x02 };
uint8_t AppEui[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t AppKey[] = { 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x66, 0x01 };

/* ABP para*/
uint8_t NwkSKey[] = { 0x15, 0xb1, 0xd0, 0xef, 0xa4, 0x63, 0xdf, 0xbe, 0x3d, 0x11, 0x18, 0x1e, 0x1e, 0xc7, 0xda, 0x85 };
uint8_t AppSKey[] = { 0xd7, 0x2c, 0x78, 0x75, 0x8c, 0xdc, 0xca, 0xbf, 0x55, 0xee, 0x4a, 0x77, 0x8d, 0x16, 0xef, 0x67 };
uint32_t DevAddr =  ( uint32_t )0x007e6ae1;

/*LoraWan channelsmask, default channels 0-7*/
uint16_t userChannelsMask[6] = { 0x00FF, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000 };

/*LoraWan Class, Class A and Class C are supported*/
DeviceClass_t  loraWanClass = CLASS_C;

/*the application data transmission duty cycle.  value in [ms].*/
uint32_t appTxDutyCycle = 15000;

/*OTAA or ABP*/
bool overTheAirActivation = true;

/*ADR enable*/
bool loraWanAdr = true;

/* Indicates if the node is sending confirmed or unconfirmed messages */
bool isTxConfirmed = true;

/* Application port */
uint8_t appPort = 2;

/*!
  Number of trials to transmit the frame, if the LoRaMAC layer did not
  receive an acknowledgment. The MAC performs a datarate adaptation,
  according to the LoRaWAN Specification V1.0.2, chapter 18.4, according
  to the following table:

  Transmission nb | Data Rate
  ----------------|-----------
  1 (first)       | DR
  2               | DR
  3               | max(DR-1,0)
  4               | max(DR-1,0)
  5               | max(DR-2,0)
  6               | max(DR-2,0)
  7               | max(DR-3,0)
  8               | max(DR-3,0)

  Note, that if NbTrials is set to 1 or 2, the MAC will not decrease
  the datarate, in case the LoRaMAC layer did not receive an acknowledgment
*/
uint8_t confirmedNbTrials = 8;

/*LoraWan debug level, select in arduino IDE tools.
  None : print basic info.
  Freq : print Tx and Rx freq, DR info.
  Freq && DIO : print Tx and Rx freq, DR, DIO0 interrupt and DIO1 interrupt info.
  Freq && DIO && PW: print Tx and Rx freq, DR, DIO0 interrupt, DIO1 interrupt, MCU sleep and MCU wake info.
*/
uint8_t debugLevel = LoRaWAN_DEBUG_LEVEL;

/*LoraWan region, select in arduino IDE tools*/
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;


/*
   Reads a 32-bit unsigned integer from Serial
*/
uint32_t readSerial() {
  uint32_t readNumber = 0;

  while (!readNumber) {
    Serial.println("Inserisci numero: ");
    readNumber = Serial.parseInt();
  }
  Serial.println("Read number: " + readNumber);
  Serial.flush();
  return readNumber;
}

/*
   appData declaration:
   uint8_t appData[LORAWAN_APP_DATA_MAX_SIZE]

   Frame structure
   | state 1 byte | reading 4 byte |
*/
static void prepareTxFrame( uint8_t port, uint32_t serialReading, uint8_t state) {

  appDataSize = 5;//AppDataSize max value is 128

  // Format the data to bytes
  appData[0] = state;

  appData[4] = serialReading & 0xFF;
  serialReading = serialReading >> 8;

  appData[3] = serialReading & 0xFF;
  serialReading = serialReading >> 8;

  appData[2] = serialReading & 0xFF;
  serialReading = serialReading >> 8;

  appData[1] = serialReading & 0xFF;

  Serial.println(appData[0]);
  Serial.println(appData[1]);
  Serial.println(appData[2]);
  Serial.println(appData[3]);
  Serial.println(appData[4]);
}

bool recording = true;

void downLinkDataHandle(McpsIndication_t *mcpsIndication) {
  String LoRa_data = "";
  Serial.printf("+REV DATA:%s,RXSIZE %d,PORT %d\r\n", mcpsIndication->RxSlot ? "RXWIN2" : "RXWIN1", mcpsIndication->BufferSize, mcpsIndication->Port);
  Serial.print("+REV DATA:");
  for (uint8_t i = 0; i < mcpsIndication->BufferSize; i++)
  {
    Serial.printf("%d", mcpsIndication->Buffer[i]);
    LoRa_data = LoRa_data + (String)(char)mcpsIndication->Buffer[i];
  }
  Serial.println();
  Serial.println(LoRa_data);

  if (LoRa_data == "Start") {
    recording = true;
  }
}

// Add your initialization code here
void setup()
{
  if (!mcuStarted) {
    LoRaWAN.displayMcuInit();
  }
  Serial.begin(115200);
  while (!Serial);
  SPI.begin(SCK, MISO, MOSI, SS);
  Mcu.init(SS, RST_LoRa, DIO0, DIO1, license);
  deviceState = DEVICE_STATE_INIT;
}


// The loop function is called in an endless loop
void loop() {
  switch ( deviceState ) {

    case DEVICE_STATE_INIT:
      // init the device
#if(LORAWAN_DEVEUI_AUTO)
      LoRaWAN.generateDeveuiByChipID();
#endif
      LoRaWAN.init(loraWanClass, loraWanRegion);
      break;

    case DEVICE_STATE_JOIN:
      // Join the net
      LoRaWAN.displayJoining();
      LoRaWAN.join();
      break;

    case DEVICE_STATE_SEND:
      if (recording) {
        LoRaWAN.displaySending();
        prepareTxFrame( appPort, readSerial(), 3 );
        LoRaWAN.send(loraWanClass);
        recording = false;
      }
      deviceState = DEVICE_STATE_CYCLE;
      break;

    case DEVICE_STATE_CYCLE:
      // Schedule next packet transmission
      txDutyCycleTime = appTxDutyCycle + randr( -APP_TX_DUTYCYCLE_RND, APP_TX_DUTYCYCLE_RND );
      LoRaWAN.cycle(txDutyCycleTime);
      deviceState = DEVICE_STATE_SLEEP;
      break;

    case DEVICE_STATE_SLEEP:
      // Puts the device to sleep
      LoRaWAN.displayAck();
      LoRaWAN.sleep(loraWanClass, debugLevel);
      break;

    default:
      deviceState = DEVICE_STATE_INIT;
      break;
  }
}
