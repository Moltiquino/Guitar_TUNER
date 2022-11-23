
int buttonpin=2;
int lpin=13;
int buttonstate=0;
int laststate=0;

void setup() {
 
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
         
  pinMode(buttonpin, INPUT);
  Serial.begin(9600);
  // put your setup code here, to run once:

}

void loop() {
  
  // put your main code here, to run repeatedly:
   buttonstate=digitalRead(buttonpin);
   if(laststate==0&&buttonstate==1)
     if(buttonstate==HIGH){
     
      digitalWrite(lpin, HIGH);
      digitalWrite(lpin+1,LOW);
      lpin--;
      delay(300);
      if(lpin==6){
        lpin=13;
       
      }
    }
   laststate=buttonstate;
  
   
  
 
}
