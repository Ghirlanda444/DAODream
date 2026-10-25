(fn PayTalent ()
  (Variabili|Predefinito|ImpostaPStamina (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPStamina) (Variabili|Predefinito|OttieniTCostNow)))
  (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniTReady) (Variabili|Predefinito|OttieniTSlot) (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniTCool)))
  (Variabili|Predefinito|ImpostaLastCombat (Utilità|Testo|GetGameTimeinSeconds)))
