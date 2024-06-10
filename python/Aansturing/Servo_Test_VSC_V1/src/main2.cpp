#include <Arduino.h>
#include "AX12A.h"




#define TX_Pin 	  (41)
#define RX_Pin 	  (40)
#define TR_Pin 	  (5)
#define BaudRate  (1000000ul)
#define S1_ID	    (3)
#define S2_ID		  (61)

// Definieer een variabele voor de pin
int position;

void setup()
{
  // Start de seriële communicatie van de ESP en de AX-12a
  Serial.begin(BaudRate);
	ax12a.begin(BaudRate, TX_Pin, RX_Pin, TR_Pin, &Serial);
//  ax12a.ledStatus(S1_ID, ON);
//  ax12a.ledStatus(S2_ID, ON);

//TODO: queue
//FIXME: queue

}

void loop()
{
  ax12a.moveSpeed(S2_ID, 0, 30);
  ax12a.ledStatus(S2_ID, ON);
  ax12a.moveSpeed(S1_ID, 0, 30);
  delay(100);
  position = ax12a.readPosition(S1_ID);
  Serial.println(position);
  delay(10000);
  
  ax12a.moveSpeed(S2_ID, 512, 30);
  ax12a.ledStatus(S2_ID, OFF);
  ax12a.moveSpeed(S1_ID, 512, 30);
  delay(100);
  position = ax12a.readPosition(S1_ID);
  Serial.println(position);
  delay(10000);
  
  ax12a.moveSpeed(S2_ID, 1023, 30);
  ax12a.ledStatus(S2_ID, ON);
  ax12a.moveSpeed(S1_ID, 1023, 30);
  delay(100);
  position = ax12a.readPosition(S1_ID);
  Serial.println(position);
  delay(10000);

  ax12a.moveSpeed(S2_ID, 512, 30);
  ax12a.ledStatus(S2_ID, OFF);
  ax12a.moveSpeed(S1_ID, 512, 30);
  delay(100);
  position = ax12a.readPosition(S1_ID);
  Serial.println(position);
  delay(10000);

}

/*
    Serial.println("Beweging starten");
  ax12a.moveSpeed(S2_ID, 1023, 30);
  ax12a.moveSpeed(S1_ID, 1023, 30);

  Serial.println("Lees posities");
  // Lees posities en controleer of het lezen succesvol is
  int positionS1 = ax12a.readPosition(S1_ID);
  int positionS2 = ax12a.readPosition(S2_ID);

  Serial.print("Positie Servo 1: ");
  if (positionS1 != -1) {
    Serial.println(positionS1);
  } else {
    Serial.println("Fout bij lezen positie S1");
  }

  Serial.print("Positie Servo 2: ");
  if (positionS2 != -1) {
    Serial.println(positionS2);
  } else {
    Serial.println("Fout bij lezen positie S2");
  }

  Serial.println("Einde van lus\n");
  
  delay(1000); // Een kleine vertraging om overlopen van de seriële buffer te voorkomen
*/