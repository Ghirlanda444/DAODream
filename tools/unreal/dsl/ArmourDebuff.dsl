(fn ArmourDebuff (Amount Seconds)
  (Variabili|Predefinito|ImpostaNArmourAdd Amount)
  (Variabili|Predefinito|ImpostaNArmourUntil (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) Seconds))
  (Funzionedichiamata|SayText :Txt "Armour broken"))
