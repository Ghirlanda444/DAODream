(fn SwitchTo ()
  (Variabili|Predefinito|ImpostaFoe (Variabili|Predefinito|OttieniHated))
  (Variabili|Predefinito|ImpostaTSwitched (Utilità|Testo|GetGameTimeinSeconds))
  (Variabili|Predefinito|ImpostaTWait (Matematica|Float|SelectFloat 0.0 (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniTWait) 5.0) (Utility|Operatori|Maggiore(>) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniTWait) 5.0) 25.0))))
