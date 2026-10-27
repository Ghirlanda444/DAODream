(fn DrawSetup ()
  (Widget|SetText(Text) (Variabili|WBP_Tactics|OttieniPresetT) (Utilità|Testo|ToText(String) "Load a preset"))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniMBeh) 0) (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniMBeh) (Utilità|Array|Length (Variabili|Predefinito|OttieniTBehavNames))))
    (:then
      (Widget|SetText(Text) (Variabili|WBP_Tactics|OttieniBehavT) (Utilità|Testo|ToText(String) (Utilità|Stringa|Append "Behaviour: " (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTBehavNames) (Variabili|Predefinito|OttieniMBeh))))))
    (:else
      (Widget|SetText(Text) (Variabili|WBP_Tactics|OttieniBehavT) (Utilità|Testo|ToText(String) "Behaviour")))))
