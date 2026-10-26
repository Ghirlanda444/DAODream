(fn Bleed (Amount Seconds)
  (Variabili|Predefinito|ImpostaBleedRate (Utility|Operatori|Dividi Amount (Matematica|Float|Max(Float) Seconds 0.1)))
  (Variabili|Predefinito|ImpostaBleedUntil (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) Seconds))
  (Funzionedichiamata|SayText :Txt "Bleeding"))
