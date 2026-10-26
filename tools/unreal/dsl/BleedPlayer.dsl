(fn BleedPlayer (Amount Seconds)
  (Variabili|Predefinito|ImpostaPBleedRate (Utility|Operatori|Dividi Amount (Matematica|Float|Max(Float) Seconds 0.1)))
  (Variabili|Predefinito|ImpostaPBleedUntil (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) Seconds))
  (Funzionedichiamata|ShowMsg :Txt "Bleeding"))
